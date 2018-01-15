<?php

namespace MuBench\ReviewSite\Controllers;


use Illuminate\Database\Eloquent\Collection;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\DetectorResult;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\ExperimentResult;
use MuBench\ReviewSite\Models\Finding;
use MuBench\ReviewSite\Models\Metadata;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\ReviewState;
use MuBench\ReviewSite\Models\Run;
use RecursiveDirectoryIterator;
use RecursiveIteratorIterator;
use Slim\Http\Request;
use Slim\Http\Response;

class RunsController extends Controller
{
    public function getIndex(Request $request, Response $response, array $args)
    {
        $experiment_id = $args['experiment_id'];
        $detector_muid = $args['detector_muid'];

        $experiment = Experiment::find($experiment_id);
        $detector = Detector::find($detector_muid);
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);

        $runs = $this->getRuns($detector, $experiment, $ex2_review_size);

        return $this->renderer->render($response, 'detector.phtml', [
            'experiment' => $experiment,
            'detector' => $detector,
            'runs' => $runs
        ]);
    }

    public function downloadRuns(Request $request, Response $response, array $args)
    {
        $experiment_id = $args['experiment_id'];
        $detector_muid = $args['detector_muid'];

        $detector = Detector::find($detector_muid);
        $experiment = Experiment::find($experiment_id);
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);

        $runs = $this->getRuns($detector, $experiment, $ex2_review_size);

        return download($response, self::exportRunStatistics($runs), $detector->muid . ".csv");
    }

    public function getResults(Request $request, Response $response, array $args)
    {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);
        $experiments = Experiment::all();

        $results = array();
        foreach($experiments as $experiment){
            $detectors = Detector::withFindings($experiment);
            $results[$experiment->id] = $this->getResultsForExperiment($experiment, $detectors, $ex2_review_size);
        }

        return $this->renderer->render($response, 'result_stats.phtml', ['results' => $results, 'ex2_review_size' => $ex2_review_size]);
    }

    public function downloadResults(Request $request, Response $response, array $args)
    {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);
        $experiment_id = $args['experiment_id'];
        $experiment = Experiment::find($experiment_id);
        $detectors = Detector::all();

        $stats = $this->getResultsForExperiment($experiment, $detectors, $ex2_review_size);
        return download($response, self::exportStatistics($experiment, $stats),
            "stats_" . $experiment->id . ".csv");
    }

    public function postRun(Request $request, Response $response, array $args)
    {
        $experimentId = $args['experiment_id'];
        $detector_muid = $args['detector_muid'];
        $project_muid = $args['project_muid'];
        $version_muid = $args['version_muid'];
        $run = decodeJsonBody($request);
        if (!$run) {
            return error_response($response,400, "empty: " . print_r($_POST, true));
        }
        $hits = $run->{'potential_hits'};
        $this->logger->info("received data for '" . $experimentId . "', '" . $detector_muid . "." . $project_muid . "." . $version_muid . "' with " . count($hits) . " potential hits.");
        $this->addRun($experimentId, $detector_muid, $project_muid, $version_muid, $run);
        $files = $request->getUploadedFiles();
        $this->logger->info("received " . count($files) . " files");
        if ($files) {
            $detector = Detector::find($detector_muid);
            foreach ($files as $img) {
                $this->handleImage($experimentId, $detector->id, $project_muid, $version_muid, $img);
            }
        }
        return $response->withStatus(200);
    }

    public function manageRuns(Request $request, Response $response)
    {
        $experiments = Experiment::all();
        $detectors = Detector::all();
        $experiment_runs = [];

        foreach($experiments as $experiment){
            $experiment_runs[$experiment->id] = [];
            foreach($detectors as $detector){
                $experiment_runs[$experiment->id][$detector->muid] = Run::of($detector)->in($experiment)->get();
            }
        }

        return $this->renderer->render($response, 'manage_runs.phtml', ['experiment_runs' => $experiment_runs]);
    }

    public function deleteRun(Request $request, Response $response, array $args)
    {
        $experimentId = $args['experiment_id'];
        $detector_muid = $args['detector_muid'];
        $project_muid = $args['project_muid'];
        $version_muid = $args['version_muid'];
        $run = Run::of(Detector::find($detector_muid))->in(Experiment::find($experimentId))->get()->where('project_muid', $project_muid)->where('version_muid', $version_muid)->first();
        if($run){
            $this->deleteRunAndRelated($run);
        }
        return $response->withRedirect($this->router->pathFor('private.manage.runs'));
    }

    static function deleteRunAndRelated(Run $run)
    {
        foreach($run->misuses as $misuse){
            foreach($misuse->reviews as $review){
                $findings_reviews = $review->finding_reviews;
                foreach($findings_reviews as $finding_review){
                    $finding_review->violation_types()->detach();
                }
                $review->finding_reviews()->delete();
                $review->reviewer()->dissociate();
            }
            $misuse->reviews()->delete();
            $misuse->metadata()->dissociate();
            $misuse->misuse_tags()->detach();
            $misuse->findings()->delete();
        }
        $run->misuses()->delete();
        $run->delete();
    }

    static function getRuns($detector, $experiment, $max_reviews)
    {
        $runs = Run::of($detector)->in($experiment)->orderBy('project_muid')->orderBy('version_muid')->get();

        foreach($runs as $run){
            $conclusive_reviews = 0;
            $filtered_misuses = new Collection;
            $misuses = $run->misuses->sortBy('misuse_muid');
            if($experiment->id === 2) {
                foreach ($misuses as $misuse) {
                    if ($conclusive_reviews >= $max_reviews) {
                        break;
                    }
                    $filtered_misuses->add($misuse);
                    if ($misuse->hasConclusiveReviewState() || (!$misuse->hasSufficientReviews() && !$misuse->hasInconclusiveReview())) {
                        $conclusive_reviews++;
                    }
                }
            }
            foreach($misuses as $misuse){
                if($misuse->metadata){
                    $filtered_misuses->add($misuse);
                }
            }
            $run->misuses = $filtered_misuses;
        }

        return $runs;
    }

    public static function exportRunStatistics($runs)
    {
        $rows = [];
        foreach ($runs as $run) {
            $run_details = [];
            $run_details["project"] = $run->project_muid;
            $run_details["version"] = $run->version_muid;
            $run_details["result"] = $run->result;
            $run_details["number_of_findings"] = $run->number_of_findings;
            $run_details["runtime"] = $run->runtime;

            foreach ($run->misuses as $misuse) {
                $row = $run_details;

                $row["misuse"] = $misuse->misuse_muid;
                $row["decision"] = $misuse->getReviewState();
                if ($misuse->hasResolutionReview()) {
                    $resolution = $misuse->getResolutionReview();
                    $row["resolution_decision"] = $resolution->getDecision();
                    $row["resolution_comment"] = escapeText($resolution->comment);
                } else {
                    $row["resolution_decision"] = "";
                    $row["resolution_comment"] = "";
                }

                $reviews = $misuse->getReviews();
                $review_index = 0;
                foreach ($reviews as $review) {
                    $review_index++;
                    $row["review{$review_index}_name"] = $review->reviewer->name;
                    $row["review{$review_index}_decision"] = $review->getDecision();
                    $row["review{$review_index}_comment"] = escapeText($review->comment);
                }

                $rows[] = $row;
            }
            if (empty($run['misuses'])) {
                $rows[] = $run_details;
            }
        }
        return createCSV($rows);
    }

    function addRun($experimentId, $detectorId, $projectId, $versionId, $run)
    {
        $detector = $this->createDetector($detectorId);
        $experiment = Experiment::find($experimentId);

        $potential_hits = $run->{'potential_hits'};

        $this->createOrUpdateRunsTable($detector, $run);
        $this->updateRun($detector, $experiment, $projectId, $versionId, $run);
        if ($potential_hits) {
            $new_run = Run::of($detector)->in($experiment)->where(['project_muid' => $projectId, 'version_muid' => $versionId])->first();
            $this->createOrUpdateFindingsTable($detector, $potential_hits);
            $this->storeFindings($detector, $experiment, $projectId, $versionId, $new_run, $potential_hits);
        }else{
            $this->createOrUpdateFindingsTable($detector, []);
        }
    }

    function createDetector($detector_muid)
    {
        $detector = Detector::find($detector_muid);
        if(!$detector){
            $detector = Detector::create(['muid' => $detector_muid]);
        }
        return $detector;
    }

    private function createOrUpdateRunsTable(Detector $detector, $run)
    {
        $propertyToColumnNameMapping = $this->getColumnNamesFromProperties($run);
        $propertyToColumnNameMapping = $this->removeDisruptiveStatsColumns($propertyToColumnNameMapping);
        $run = new \MuBench\ReviewSite\Models\Run;
        $run->setDetector($detector);
        $this->createOrUpdateTable($run->getTable(), $propertyToColumnNameMapping, array($this, 'createRunsTable'));
    }

    private function createOrUpdateFindingsTable(Detector $detector, $findings)
    {
        $propertyToColumnNameMapping = $this->getPropertyToColumnNameMapping($findings);
        $propertyToColumnNameMapping = $this->removeDisruptiveFindingsColumns($propertyToColumnNameMapping);
        $finding = new \MuBench\ReviewSite\Models\Finding;
        $finding->setDetector($detector);
        $this->createOrUpdateTable($finding->getTable(), $propertyToColumnNameMapping, array($this, 'createFindingsTable'));
    }

    private function createOrUpdateTable($table_name, $propertyToColumnNameMapping, $createFunc)
    {
        if (!Schema::hasTable($table_name)) {
            $createFunc($table_name);
        }
        $existing_columns = $this->getPropertyColumnNames($table_name);
        foreach ($propertyToColumnNameMapping as $column) {
            if (!in_array($column, $existing_columns)) {
                $this->addColumnToTable($table_name, $column);
            }
        }
    }

    private function getPropertyColumnNames($table_name)
    {
        return Schema::getColumnListing($table_name);
    }

    /** @noinspection PhpUnusedPrivateMethodInspection used in createOrUpdateFindingsTable */
    private function createFindingsTable($table_name)
    {
        Schema::create($table_name, function (Blueprint $table) {
            $table->increments('id');
            $table->integer('experiment_id');
            $table->integer('misuse_id');
            $table->string('project_muid', 30);
            $table->string('version_muid', 30);
            $table->string('misuse_muid', 30);
            $table->integer('startline')->nullable();
            $table->integer('rank');
            $table->text('file')->nullable();
            $table->text('method')->nullable();
            $table->dateTime('created_at');
            $table->dateTime('updated_at');
        });
    }

    /** @noinspection PhpUnusedPrivateMethodInspection used in createOrUpdateRunsTable */
    private function createRunsTable($table_name)
    {
        Schema::create($table_name, function (Blueprint $table) {
            $table->increments('id');
            $table->integer('experiment_id');
            $table->string('project_muid', 30);
            $table->string('version_muid', 30);
            $table->float('runtime');
            $table->integer('number_of_findings');
            $table->string('result', 30);
            $table->dateTime('created_at');
            $table->dateTime('updated_at');
        });
    }

    private function getPropertyToColumnNameMapping($entries)
    {
        $propertyToColumnNameMapping = [];
        foreach ($entries as $entry) {
            $propertyToColumnName = $this->getColumnNamesFromProperties($entry);
            foreach ($propertyToColumnName as $property => $column) {
                $propertyToColumnNameMapping[$property] = $column;
            }
        }
        return $propertyToColumnNameMapping;
    }

    private function getColumnNamesFromProperties($entry)
    {
        $propertyToColumnNameMapping = [];
        $properties = array_keys(get_object_vars($entry));
        foreach ($properties as $property) {
            // MySQL does not permit column names with more than 64 characters:
            // https://dev.mysql.com/doc/refman/5.7/en/identifiers.html
            $column_name = strlen($property) > 64 ? substr($property, 0, 64) : $property;
            // Remove . from column names, since it may be confused with a table-qualified name.
            $column_name = str_replace('.', ':', $column_name);
            $propertyToColumnNameMapping[$property] = $column_name;
        }
        return $propertyToColumnNameMapping;
    }

    private function removeDisruptiveStatsColumns($columns)
    {
        unset($columns["potential_hits"]);
        unset($columns["detector"]);
        return $columns;
    }

    private function removeDisruptiveFindingsColumns($columns)
    {
        unset($columns["id"]);
        unset($columns["target_snippets"]);
        return $columns;
    }

    private function addColumnToTable($table_name, $column)
    {
        Schema::table($table_name, function ($table) use ($column) {
            $table->text($column)->nullable();
        });
    }

    private function storeFindings(Detector $detector, Experiment $experiment, $projectId, $versionId, Run $run, $findings)
    {
        foreach ($findings as $finding) {
            $misuseId = $finding->{'misuse'};
            $misuse = $run->misuses()->where('misuse_muid', $misuseId)->first();
            if(!$misuse){
                $misuse = $this->createMisuse($detector, $experiment, $projectId, $versionId, $misuseId, $run->id);
            }
            $this->storeFinding($detector, $experiment, $projectId, $versionId, $misuseId, $misuse, $finding);
            if ($experiment->id === 2) {
                $this->storeFindingTargetSnippets($projectId, $versionId, $misuseId, $finding->{'file'}, $finding->{'target_snippets'});
            }
        }
    }

    private function createMisuse(Detector $detector, Experiment $experiment, $projectId, $versionId, $misuseId, $runId)
    {
        if ($experiment->id == 1 || $experiment->id == 3) {
            $metadata = Metadata::where(['project_muid' => $projectId, 'version_muid' => $versionId, 'misuse_muid' => $misuseId])->first();
            if($metadata){
                $misuse = Misuse::create(['metadata_id' => $metadata->id, 'misuse_muid' => $misuseId, 'run_id' => $runId, 'detector_muid' => $detector->muid]);
            } else {
                $misuse = Misuse::create(['misuse_muid' => $misuseId, 'run_id' => $runId, 'detector_muid' => $detector->muid]);
            }
        } else {
            $misuse = Misuse::create(['misuse_muid' => $misuseId, 'run_id' => $runId, 'detector_muid' => $detector->muid]);
        }
        return $misuse;
    }

    private function storeFinding(Detector $detector, $experiment, $projectId, $versionId, $misuseId, $misuse, $finding)
    {
        $values = array('project_muid' => $projectId, 'version_muid' => $versionId, 'misuse_muid' => $misuseId, 'misuse_id' => $misuse->id, 'experiment_id' => $experiment->id);
        $propertyToColumnNameMapping = $this->getPropertyToColumnNameMapping([$finding]);
        $propertyToColumnNameMapping = $this->removeDisruptiveFindingsColumns($propertyToColumnNameMapping);
        foreach ($propertyToColumnNameMapping as $property => $column) {
            $value = $finding->{$property};
            $values[$column] = $value;
        }
        $finding = new Finding;
        $finding->setDetector($detector);
        foreach($values as $key => $value){
            $finding[$key] = $value;
        }
        $finding->save();
    }

    private function updateRun(Detector $detector, Experiment $experiment, $projectId, $versionId, $run)
    {
        $savedRun = Run::of($detector)->in($experiment)->where(['project_muid' => $projectId, 'version_muid' => $versionId])->first();
        if (!$savedRun) {
            $savedRun = new \MuBench\ReviewSite\Models\Run;
            $savedRun->setDetector($detector);
            $savedRun->experiment_id = $experiment->id;
            $savedRun->project_muid = $projectId;
            $savedRun->version_muid = $versionId;
        }
        $propertyToColumnNameMapping = $this->getColumnNamesFromProperties($run);
        $propertyToColumnNameMapping = $this->removeDisruptiveStatsColumns($propertyToColumnNameMapping);
        foreach ($propertyToColumnNameMapping as $property => $column) {
            $value = $run->{$property};
            $savedRun[$column] = $value;
        }
        $savedRun->save();
    }

    private function storeFindingTargetSnippets($projectId, $versionId, $misuseId, $file, $snippets)
    {
        foreach ($snippets as $snippet) {
            SnippetsController::createSnippet($projectId, $versionId, $misuseId, $file, $snippet->{'first_line_number'}, $snippet->{'code'});
        }
    }

    function getResultsForExperiment($experiment, $detectors, $ex2_review_size)
    {
        $results = array();
        foreach($detectors as $detector){
            $runs = Run::of($detector)->in($experiment)->get();
            foreach ($runs as &$run) {
                $misuses = $run->misuses->sortBy('misuse_muid');
                $filtered_misuses = new Collection;
                if($experiment->id === 1){
                    foreach ($misuses as $misuse) {
                        if (!is_null($misuse->metadata) && !$misuse->metadata->patterns->isEmpty()) {
                            $filtered_misuses->add($misuse);
                        }
                    }
                }elseif($experiment->id === 3){
                    foreach ($misuses as $misuse) {
                        if (!is_null($misuse->metadata)) {
                            $filtered_misuses->add($misuse);
                        }
                    }
                }elseif($experiment->id === 2 && $ex2_review_size > -1){
                    $number_of_misuses = 0;
                    foreach ($misuses as $misuse) {
                        if ($misuse->getReviewState() != ReviewState::UNRESOLVED) {
                            $filtered_misuses->add($misuse);
                            $number_of_misuses++;
                        }

                        if ($number_of_misuses == $ex2_review_size) {
                            break;
                        }
                    }
                }
                $run->misuses = $filtered_misuses;
            }
            $results[$detector->muid] = new DetectorResult($detector, $runs);
        }
        $results["total"] = new ExperimentResult($results);
        return $results;
    }

    public static function exportStatistics($experiment, $stats)
    {
        $rows = [];
        foreach ($stats as $stat) {
            $row = [];
            $row["detector"] = $stat->getDisplayName();
            $row["project"] = $stat->number_of_projects;

            if ($experiment->id === 1) {
                $row["synthetics"] = $stat->number_of_synthetics;
            }
            if ($experiment->id === 1 || $experiment->id === 3) {
                $row["misuses"] = $stat->number_of_misuses;
            }

            $row["potential_hits"] = $stat->misuses_to_review;
            $row["open_reviews"] = $stat->open_reviews;
            $row["need_clarification"] = $stat->number_of_needs_clarification;
            $row["yes_agreements"] = $stat->yes_agreements;
            $row["no_agreements"] = $stat->no_agreements;
            $row["total_agreements"] = $stat->getNumberOfAgreements();
            $row["yes_no_agreements"] = $stat->yes_no_disagreements;
            $row["no_yes_agreements"] = $stat->no_yes_disagreements;
            $row["total_disagreements"] = $stat->getNumberOfDisagreements();
            $row["kappa_p0"] = $stat->getKappaP0();
            $row["kappa_pe"] = $stat->getKappaPe();
            $row["kappa_score"] = $stat->getKappaScore();
            $row["hits"] = $stat->number_of_hits;

            if ($experiment->id === 2) {
                $row["precision"] = $stat->getPrecision();
            } else {
                $row["recall"] = $stat->getRecall();
            }

            $rows[] = $row;
        }
        return createCSV($rows);
    }

    private function handleImage($experimentId, $detectorId, $projectId, $versionId, $img){
        $path = $this->settings['upload'] . "/$experimentId/$detectorId/$projectId/$versionId/";
        $file = $path . $img->getClientFilename();
        $this->logger->info("moving file " . $img->getClientFilename() . " to " . $path);
        if(file_exists($file)) {
            unlink($file);
        }
        mkdir($path, 0755, true);
        $img->moveTo($file);
    }
}
