<?php

namespace MuBench\ReviewSite\Controllers;


use Illuminate\Database\Eloquent\Model;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\Run;
use MuBench\ReviewSite\Models\Snippet;
use MuBench\ReviewSite\Models\Violation;
use Slim\Http\Request;
use Slim\Http\Response;

class ImportRunsController extends RunsController
{

    public function getImport(Request $request, Response $response)
    {
        return $this->renderer->render($response, 'import_db.phtml');
    }

    public function postImport(Request $request, Response $response, array $args)
    {
        $experiment_id = $args['experiment_id'];
        $detector_muid = $args['detector_muid'];

        $formdata = $request->getParsedBody();
        $project_muid = $formdata['project_muid'];
        $version_muid = $formdata['version_muid'];

        $host = $formdata['host'];
        $database = $formdata['database'];
        $username = $formdata['username'];
        $password = $formdata['password'];
        $prefix = $formdata['prefix'];

        $connection = $this->createNewDBConnection($host, $database, $username, $password, $prefix);
        if($connection){
            $this->importRunsFromConnection($experiment_id, $detector_muid, $project_muid, $version_muid, $connection);
            return $response->withJson("success",200);
        }
        return $response->withJson("failure: could not connect to db",500);
    }

    private function createNewDBConnection($host, $database, $username, $password, $prefix)
    {
        $this->capsule->addConnection([
            'driver' => 'mysql',
            'host' => $host,
            'database' => $database,
            'username' => $username,
            'password' => $password,
            'charset' => 'utf8',
            'collation' => 'utf8_unicode_ci',
            'prefix' => $prefix,
        ], 'extern');
        return $this->capsule->getConnection('extern');
    }

    function importRunsFromConnection($experiment_id, $detector_muid, $project_muid, $version_muid, $connection)
    {
        list($local_detector, $detector) = $this->getLocalAndExternalDetector($detector_muid, $connection);

        $run = new Run;
        $run->setDetector($detector);
        $run->setConnection($connection->getName());

        if ($project_muid != "" && $version_muid != "") {
            $runs = $run->in(Experiment::find($experiment_id))->where([ 'project_muid' => $project_muid, 'version_muid' => $version_muid])->get();
        } else {
            $runs = $run->in(Experiment::find($experiment_id))->get();
        }
        foreach ($runs as $run) {
            $imported_run = $this->importRun($local_detector, $run);

            foreach ($run->misuses as $misuse) {
                $this->importFullMisuse($local_detector, $imported_run, $misuse, $connection);
            }
        }
    }

    private function getLocalAndExternalDetector($detector_muid, $connection): array
    {
        $local_detector = $this->getOrCreateDetector($detector_muid);
        $detector = new Detector;
        $detector->setConnection($connection->getName());
        $detector = $detector->find($detector_muid);
        return array($local_detector, $detector);
    }

    private function importRun($detector, $run)
    {
        $this->createOrUpdateRunsTable($detector, $run->getAttributes());
        $imported_run = $this->importAndResetConnectionModel($run);
        $imported_run->setDetector($detector);
        $imported_run->save();
        return $imported_run;
    }

    private function importAndResetConnectionModel(Model $model){
        $imported_model = $model->replicate();
        $imported_model->setConnection('default');
        return $imported_model;
    }

    private function importFullMisuse($local_detector, $imported_run, $misuse, $connection)
    {
        $imported_misuse = $imported_run->misuses()->where('misuse_muid', $misuse->misuse_muid)->first();
        if (!$imported_misuse) {
            list($imported_misuse, $imported_metadata) = $this->importMisuseAndMetadata($misuse, $imported_run, $local_detector);
        }

        $this->importMisuseFindings($misuse->findings, $local_detector, $imported_misuse);

        $this->importMisuseSnippets($connection, $misuse);

        if ($misuse->metadata) {
            $violations = $this->importMetadataCorrentUsagesAndViolations($misuse, $imported_metadata);
            $imported_metadata->violations()->sync($violations);
        }

        $tag_ids = $this->importTags($misuse);
        $imported_misuse->misuse_tags()->sync($tag_ids);

        foreach ($misuse->reviews as $review) {
            $this->importReviews($review, $imported_misuse);
        }
    }


    private function importReviews($review, $imported_misuse)
    {
        $reviewer = Reviewer::firstOrCreate(['name' => $review->reviewer->name]);
        $imported_review = $this->importAndResetConnectionModel($review);
        $imported_review->misuse_id = $imported_misuse->id;
        $imported_review->reviewer_id = $reviewer->id;
        $imported_review->save();
        foreach ($review->finding_reviews as $finding_review) {
            $imported_finding_review = $this->importAndResetConnectionModel($finding_review);
            $imported_finding_review->review_id = $imported_review->id;
            $imported_finding_review->save();
            $types = [];
            foreach ($finding_review->violations as $type) {
                $type = Violation::firstOrCreate(['name' => $type->name]);
                $types[] = $type->id;
            }
            $imported_finding_review->violations()->sync($types);
        }
    }

    private function importTags($misuse): array
    {
        $tag_ids = [];
        foreach ($misuse->misuse_tags as $tag) {
            $imported_tag = $this->importAndResetConnectionModel($tag);
            $imported_tag->save();
            $tag_ids[] = $imported_tag->id;
        }
        return $tag_ids;
    }

    private function importMetadataCorrentUsagesAndViolations($misuse, $imported_metadata): array
    {
        foreach ($misuse->metadata->correct_usages as $pattern) {
            $imported_pattern = $this->importAndResetConnectionModel($pattern);
            $imported_pattern->metadata_id = $imported_metadata->id;
            $imported_pattern->save();
        }
        $violations = [];
        foreach ($misuse->metadata->violations as $type) {
            $imported_type = $this->importAndResetConnectionModel($type);
            $imported_type->save();
            $violations[] = $imported_type->id;
        }
        return $violations;
    }

    private function importMisuseSnippets($connection, $misuse)
    {
        $snippet = new Snippet;
        $snippet->setConnection($connection->getName());
        $snippets = $snippet->of($misuse->getProject(), $misuse->getVersion(), $misuse->misuse_muid, $misuse->getFile())->get();
        foreach ($snippets as $snippet) {
            $imported_snippet = $this->importAndResetConnectionModel($snippet);
            $imported_snippet->save();
        }
    }

    private function importMisuseFindings($findings, $detector, $misuse)
    {
        $this->createOrUpdateFindingsTable($detector, $findings->toArray());
        foreach ($findings as $finding) {
            $imported_finding = $this->importAndResetConnectionModel($finding);
            $imported_finding->setDetector($detector);
            $imported_finding->misuse_id = $misuse->id;
            $imported_finding->save();
        }
    }

    private function importMisuseAndMetadata($misuse, $run, $detector): array
    {
        $imported_misuse = $this->importAndResetConnectionModel($misuse);
        $imported_misuse->run_id = $run->id;
        $imported_metadata = null;
        if ($misuse->metadata) {
            $imported_metadata = $this->importAndResetConnectionModel($misuse->metadata);
            $imported_metadata->save();
            $imported_misuse->metadata_id = $imported_metadata->id;
        }
        $imported_misuse->detector_id = $detector->id;
        $imported_misuse->save();
        return array($imported_misuse, $imported_metadata);
    }

}
