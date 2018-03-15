<?php


use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;

require_once "SlimTestCase.php";

class DetectorTest extends SlimTestCase
{
    /**
     * @var RunsController
     */
    private $runs_controller;

    private $run_without_findings;

    public function setUp()
    {
        parent::setUp();

        $this->runs_controller = new RunsController($this->container);
        $this->run_without_findings = [
            'result' => 'error',
            'runtime' => 42,
            'number_of_findings' => 0,
            'potential_hits' => [],
            'timestamp' => 1337
        ];
    }

    function test_detectors_with_runs__none()
    {
        $this->runs_controller->addRun(1, '-d-', '-p-', '-v-', $this->run_without_findings);
        $experiment = Experiment::find(2);

        $detectorsWithRuns = Detector::withRuns($experiment);

        self::assertEmpty($detectorsWithRuns);
    }

    function test_detectors_with_runs__exists()
    {
        $this->runs_controller->addRun(1, 'test_detector', '-p-', '-v-', $this->run_without_findings);
        $experiment = Experiment::find(1);

        $detectorsWithRuns = Detector::withRuns($experiment);

        self::assertNotEmpty($detectorsWithRuns);
        self::assertEquals('test_detector', $detectorsWithRuns[0]->muid);
    }

    function test_detectors_with_findings__none()
    {
        $this->runs_controller->addRun(1, 'test_detector', '-p-', '-v-', $this->run_without_findings);
        $experiment = Experiment::find(1);

        $detectorsWithFindings = Detector::withFindings($experiment);

        self::assertEmpty($detectorsWithFindings);
    }

    function test_detectors_with_findings__exists()
    {
        $run_with_findings = [
            'result' => 'success',
            'runtime' => 42,
            'number_of_findings' => 1,
            'potential_hits' => [['misuse' => '-m-', 'rank' => 1337]],
            'timestamp' => 1337
        ];
        $this->runs_controller->addRun(1, 'test_detector', '-p-', '-v-', $run_with_findings);
        $experiment = Experiment::find(1);

        $detectorsWithFindings = Detector::withFindings($experiment);

        self::assertNotEmpty($detectorsWithFindings);
    }
}
