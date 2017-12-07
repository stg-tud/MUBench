<?php

require_once "SlimTestCase.php";

use Illuminate\Database\Eloquent\Collection;
use MuBench\ReviewSite\Controllers\FindingsController;
use MuBench\ReviewSite\Controllers\FindingsUploader;
use MuBench\ReviewSite\Controllers\MetadataController;
use MuBench\ReviewSite\Controllers\ReviewsController;
use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Controllers\SnippetUploader;
use MuBench\ReviewSite\Controllers\MisuseTagsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\DetectorResult;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\ExperimentResult;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\Run;

class RunsControllerTest extends SlimTestCase
{
    private $request_body;

    /** @var  Detector */
    private $detector1;

    /** @var  Detector */
    private $detector2;

    function setUp()
    {
        parent::setUp();
        parent::setUp();
        $this->runsController = new RunsController($this->container);
        $this->detector1 = Detector::create(['muid' => '-d1-']);
        $this->detector2 = Detector::create(['muid' => '-d2-']);
        $this->request_body = json_decode(json_encode([
            "result" => "success",
            "runtime" => 42.1,
            "number_of_findings" => 23,
            "-custom-stat-" => "-stat-val-",
            "potential_hits" => [
                [
                    "misuse" => "-m-",
                    "rank" => 0,
                    "target_snippets" => [
                        ["first_line_number" => 6, "code" => "-code-"]
                    ],
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ],
                [
                    "misuse" => "-m-",
                    "rank" => 2,
                    "target_snippets" => [
                        ["first_line_number" => 5, "code" => "-code-"]
                    ],
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]]
        ]));
    }

    function test_detector_creation(){
        Detector::create(['muid' => '-d3-']);
        Detector::create(['muid' => '-d4-']);
        $detector = Detector::find('-d3-');
        $detector2 = Detector::find('-d4-');
        self::assertEquals(3, $detector->id);
        self::assertEquals(4, $detector2->id);
    }

    function test_store_ex1()
    {

        $this->runsController->addRun(1, '-d-', '-p-', '-v-',  $this->request_body);
        $detector = Detector::where('muid', '=', '-d-')->first();
        $run = Run::of($detector)->in(Experiment::find(1))->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();

        self::assertEquals('success', $run->result);
        self::assertEquals(42.1, $run->runtime);
        self::assertEquals(23, $run->number_of_findings);
        self::assertEquals('-stat-val-', $run["-custom-stat-"]);
        self::assertEquals(1, sizeof($run->misuses));
        self::assertEquals(null, sizeof($run->misuses[0]->metadata_id));
    }

    function test_store_ex2()
    {
        $this->runsController->addRun(2, '-d-', '-p-', '-v-', $this->request_body);
        $detector = Detector::where('muid', '=', '-d-')->first();
        $run = Run::of($detector)->in(Experiment::find(2))->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();

        self::assertEquals(1, sizeof($run->misuses));
        self::assertEquals(2, sizeof($run->misuses[0]->findings));
        self::assertEquals(2, sizeof($run->misuses[0]->snippets()));

        $misuse = $run->misuses[0];
        $finding = $misuse->findings[0];
        $snippet = $misuse->snippets()[0];

        self::assertEquals('success', $run->result);
        self::assertEquals(42.1, $run->runtime);
        self::assertEquals(23, $run->number_of_findings);
        self::assertEquals('-stat-val-', $run["-custom-stat-"]);
        self::assertEquals($detector->muid, $misuse->detector_muid);
        self::assertEquals('-m-', $misuse->misuse_muid);
        self::assertEquals(null, $misuse->metadata_id);
        self::assertEquals($run->id, $misuse->run_id);
        self::assertEquals('-p-', $finding->project_muid);
        self::assertEquals('-v-', $finding->version_muid);
        self::assertEquals('-m-', $finding->misuse_muid);
        self::assertEquals('0', $finding->rank);
        self::assertEquals('-val1-', $finding['custom1']);
        self::assertEquals('-val2-', $finding['custom2']);
        self::assertEquals('-code-', $snippet->snippet);
        self::assertEquals('5', $snippet->line);
    }

    function test_store_ex3()
    {
        $this->runsController->addRun(3, '-d-', '-p-', '-v-', $this->request_body);
        $detector = Detector::where('muid', '=', '-d-')->first();
        $run = Run::of($detector)->in(Experiment::find(3))->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();

        self::assertEquals('success', $run->result);
        self::assertEquals(42.1, $run->runtime);
        self::assertEquals(23, $run->number_of_findings);
        self::assertEquals('-stat-val-', $run["-custom-stat-"]);
    }

    function test_get_misuse_ex1(){
        $metadataController = new MetadataController($this->container);
        // SMELL currently, this test depends on a pattern in the metadata, because otherwise the metadata is not
        // found for ex1. This should not be necessary anymore, once the findings controller is separated.
        $metadataController->updateMetadata('-p-', '-v-', '-m-', '-desc-',
            ['diff-url' => '-diff-', 'description' => '-fix-desc-'],
            ['file' => '-file-location-', 'method' => '-method-location-'], [],
            [['id' => '-p1-', 'snippet' => ['code' => '-code-', 'first_line' => 42]]], []);

        $this->runsController->addRun(1, '-d-', '-p-', '-v-', json_decode(<<<EOT
    {
        "result": "success",
        "runtime": 42.1,
        "number_of_findings": 23,
        "potential_hits": [
            {
                "misuse": "-m-",
                "rank": 0,
                "target_snippets": [
                    {"first_line_number": 5, "code": "-code-"}
                ],
                "custom1": "-val1-",
                "custom2": "-val2-"
            }
        ]
    }
EOT
        ));

        $detector = Detector::where('muid', '=', '-d-')->first();
        $run = Run::of($detector)->in(Experiment::find(1))->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();

        self::assertNotNull($run->misuses[0]->metadata_id);
    }

    public function test_ex1_stats_as_csv()
    {
        $experiment = Experiment::find(1);
        $run1 = $this->createSomeRun(1, $experiment, $this->detector1, [[[]]]);
        $run2 = $this->createSomeRun(2, $experiment, $this->detector2, [[['Yes', 'Yes']]]);
        $stats = [
            new DetectorResult(
                $this->detector1
                , new Collection([$run1])),
            new DetectorResult(
                $this->detector2
                , new Collection([$run2]))];
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = $this->createCSV(["detector,project,synthetics,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall",
            "-d1-,1,0,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0",
            "-d2-,1,0,1,1,0,0,1,0,1,0,0,0,1,0,1,1,1",
            "Total,1,0,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,0.5"]);
        self::assertEquals($expected_csv, RunsController::exportStatistics($experiment, $stats));
    }

    public function test_ex2_stats_as_csv()
    {
        $experiment = Experiment::find(2);
        $run1 = $this->createSomeRun(1, $experiment, $this->detector1, [[[]]]);
        $run2 = $this->createSomeRun(2, $experiment, $this->detector2, [[['Yes', 'Yes']]]);
        $stats = [
            new DetectorResult(
                $this->detector1
                , new Collection([$run1])),
            new DetectorResult(
                $this->detector2
                , new Collection([$run2]))];
        $stats["total"] = new ExperimentResult($stats);
        $expected_csv = $this->createCSV(["detector,project,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,precision",
            "-d1-,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0",
            "-d2-,1,1,0,0,1,0,1,0,0,0,1,0,1,1,1",
            "Total,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,0.5"]);
        self::assertEquals($expected_csv, RunsController::exportStatistics($experiment, $stats));
    }

    public function test_ex3_stats_as_csv()
    {
        $experiment = Experiment::find(3);
        $run1 = $this->createSomeRun(1, $experiment, $this->detector1, [[[]]]);
        $run2 = $this->createSomeRun(2, $experiment, $this->detector2, [[['Yes', 'Yes']]]);
        $stats = [
            new DetectorResult(
                $this->detector1
                , new Collection([$run1])),
            new DetectorResult(
                $this->detector2
                , new Collection([$run2]))];
        $stats["total"] = new ExperimentResult($stats);
        $expected_csv = $this->createCSV([
            "detector,project,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall",
            "-d1-,1,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0",
            "-d2-,1,1,1,0,0,1,0,1,0,0,0,1,0,1,1,1",
            "Total,1,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,0.5"
        ]);

        self::assertEquals($expected_csv, RunsController::exportStatistics($experiment, $stats));
    }

    function test_export_detector_run_as_csv()
    {
        $experiment = Experiment::find(1);
        $run = $this->createSomeRun(1, $experiment, $this->detector1, [[['Yes', 'Yes']], [['Yes', 'No'], 'Yes'], [[]]]);
        $runs = [$run];
        $expected_csv = $this->createCSV([
            "project,version,result,number_of_findings,runtime,misuse,decision,resolution_decision,resolution_comment,review1_name,review1_decision,review1_comment,review2_name,review2_decision,review2_comment",
            "-p-,-v-,success,23,42.1,0,4,,,-reviewer0-,2,\"-comment-\",-reviewer1-,2,\"-comment-\"",
            "-p-,-v-,success,23,42.1,1,6,2,\"-comment-\",-reviewer0-,2,\"-comment-\",-reviewer1-,0,\"-comment-\"",
            "-p-,-v-,success,23,42.1,2,1,,"
        ]);

        self::assertEquals($expected_csv, RunsController::exportRunStatistics($runs));
    }

    private function createSomeRun($id, Experiment $experiment, Detector $detector, $misuses)
    {
        $run = new \MuBench\ReviewSite\Models\Run;
        $run->setDetector($detector);
        $run->id = $id;
        $run->experiment_id = $experiment->id;
        $run->project_muid = '-p-';
        $run->version_muid = '-v-';
        $run->result = 'success';
        $run->number_of_findings = 23;
        $run->runtime = 42.1;
        $run->misuses = new Collection;
        foreach($misuses as $key => $misuse){
            $new_misuse = Misuse::create(['misuse_muid' => $key, 'run_id' => $run->id, 'detector_muid' => $detector->muid]);
            $this->createFindingWith($experiment, $detector, $new_misuse);
            $this->addReviewsForMisuse($new_misuse, $misuse[0], sizeof($misuse) > 1 ? $misuse[1] : null);
            $new_misuse->findings;
            $new_misuse->save();
            $run->misuses->push($new_misuse);
        }
        return $run;
    }

    private function addReviewsForMisuse($misuse, $decisions, $resolutionDecision = null)
    {
        $reviewController = new ReviewsController($this->container);
        foreach ($decisions as $index => $decision) {
            $reviewer = Reviewer::firstOrCreate(['name' => '-reviewer' . $index . '-']);
            $reviewController->updateOrCreateReview($misuse->id, $reviewer->id, '-comment-', [['hit' => $decision, 'types' => []]]);
        }

        if ($resolutionDecision) {
            $resolutionReviewer = Reviewer::where(['name' => 'resolution'])->first();
            $reviewController->updateOrCreateReview($misuse->id, $resolutionReviewer->id, '-comment-', [['hit' => $resolutionDecision, 'types' => []]]);
        }
    }

    private function createCSV($lines)
    {
        array_unshift($lines, "sep=,");
        return implode("\n", $lines);
    }
}
