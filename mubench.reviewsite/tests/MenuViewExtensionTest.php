<?php

use MuBench\ReviewSite\Controllers\ReviewsController;
use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Extensions\MenuViewExtension;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\ReviewState;
use MuBench\ReviewSite\Models\Run;

require_once "SlimTestCase.php";


class MenuViewExtensionTest extends SlimTestCase
{
    private $run_with_two_potential_hits_for_one_misuse;

    /** @var  Detector */
    private $detector;

    /**@var Experiment */
    private $experiment;

    /**@var Run */
    private $run;

    /**@var ReviewsController */
    private $reviewController;

    /**@var Reviewer */
    private $reviewer1;

    /**@var Reviewer */
    private $reviewer2;

    function setUp()
    {
        parent::setUp();
        $this->detector = Detector::create(['muid' => '-d-']);
        $this->experiment = Experiment::find(2);
        $runsController = new RunsController($this->container);
        $runsController->addRun($this->experiment->id, $this->detector->muid, '-p-', '-v-',  [
            "result" => "success",
            "runtime" => 42.1,
            "number_of_findings" => 23,
            "timestamp" => 12,
            "potential_hits" => [
                [
                    "misuse" => "-m-",
                    "rank" => 0,
                    "target_snippets" => [],
                    "file" => "//src/file",
                ]]
        ]);
        $this->run = Run::of($this->detector)->in($this->experiment)->first();
        $this->reviewController = new ReviewsController($this->container);
        $this->reviewer1 = Reviewer::create(['name' => "r1"]);
        $this->reviewer2 = Reviewer::create(['name' => "r2"]);
    }

    function testDetectorNeedsReviewGlobalAndPersonal()
    {
        $menuViewExntesion = new MenuViewExtension($this->container);
        $review_states = $menuViewExntesion->getReviewStates($this->experiment, $this->detector, 20, $this->reviewer1);
        self::assertEquals([ReviewState::NEEDS_REVIEW=>["global" => true, "personal" => true], ReviewState::NEEDS_CLARIFICATION=>false, ReviewState::DISAGREEMENT=>false], $review_states);
    }

    function testDetectorNeedsReviewGlobalNotPersonal()
    {
        $this->reviewController->updateOrCreateReview($this->run->misuses[0]->id, $this->reviewer1->id, '-comment-', [['hit' => "Yes", 'types' => []]]);

        $menuViewExntesion = new MenuViewExtension($this->container);
        $review_states = $menuViewExntesion->getReviewStates($this->experiment, $this->detector, 20, $this->reviewer1);
        self::assertEquals([ReviewState::NEEDS_REVIEW=>["global" => true, "personal" => false], ReviewState::NEEDS_CLARIFICATION=>false, ReviewState::DISAGREEMENT=>false], $review_states);
    }

    function testDetectorNeedsClarification()
    {
        $this->reviewMisuse("?", "?");
        $menuViewExntesion = new MenuViewExtension($this->container);
        $review_states = $menuViewExntesion->getReviewStates($this->experiment, $this->detector, 20, $this->reviewer1);
        self::assertEquals([ReviewState::NEEDS_REVIEW=>["global" => false, "personal" => false], ReviewState::NEEDS_CLARIFICATION=>true, ReviewState::DISAGREEMENT=>false], $review_states);
    }

    function testDetectorDisagreement()
    {
        $this->reviewMisuse("No", "Yes");
        $menuViewExntesion = new MenuViewExtension($this->container);
        $review_states = $menuViewExntesion->getReviewStates($this->experiment, $this->detector, 20, $this->reviewer1);
        self::assertEquals([ReviewState::NEEDS_REVIEW=>["global" => false, "personal" => false], ReviewState::NEEDS_CLARIFICATION=>false, ReviewState::DISAGREEMENT=>true], $review_states);
    }

    private function reviewMisuse($reviewer1_decision, $reviewer2_decision)
    {
        $this->reviewController->updateOrCreateReview($this->run->misuses[0]->id, $this->reviewer1->id, '-comment-', [['hit' => $reviewer1_decision, 'types' => []]]);
        $this->reviewController->updateOrCreateReview($this->run->misuses[0]->id, $this->reviewer2->id, '-comment-', [['hit' => $reviewer2_decision, 'types' => []]]);
    }

}
