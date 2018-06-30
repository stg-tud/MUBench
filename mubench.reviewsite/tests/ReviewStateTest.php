<?php

namespace MuBench\ReviewSite\Tests;

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use MuBench\ReviewSite\Controllers\ReviewsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\ReviewState;

class ReviewStateTest extends SlimTestCase
{

    /** @var  ReviewsControllerHelper */
    private $reviewsControllerHelper;

    /** @var  Detector */
    private $detector;

    function setUp()
    {
        parent::setUp();
        $this->reviewsControllerHelper = new ReviewsControllerHelper($this->container);
        $this->detector = Detector::create(['muid' => 'test-detector']);
    }

    function test_no_potential_hits()
    {
        $misuse = Misuse::create(['misuse_muid' => "test", 'run_id' => 1, 'detector_id' => $this->detector->id]);
        $finding = new \MuBench\ReviewSite\Models\Finding;
        $finding->setDetector($this->detector);
        Schema::create($finding->getTable(), function (Blueprint $table) {
            $table->increments('id');
            $table->integer('experiment_id');
            $table->integer('misuse_id');
            $table->string('project_muid', 30);
            $table->string('version_muid', 30);
            $table->string('misuse_muid', 30);
            $table->integer('startline');
            $table->integer('rank');
            $table->integer('additional_column')->nullable();
            $table->text('file');
            $table->text('method');
            $table->dateTime('created_at');
            $table->dateTime('updated_at');
        });
        self::assertEquals(ReviewState::NOTHING_TO_REVIEW, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_needs_2_reviews()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions([/* none */]);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_needs_1_review()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes']);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_needs_review_overrules_needs_carification()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['?']);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_agreement_yes()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'Yes']);

        self::assertEquals(ReviewState::AGREEMENT_YES, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_agreement_no()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['No', 'No']);

        self::assertEquals(ReviewState::AGREEMENT_NO, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_disagreement()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'No']);

        self::assertEquals(ReviewState::DISAGREEMENT, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_needs_clarification()
    {
        // NEEDS_REVIEW takes precedence over NEEDS_CLARIFICATION, hence, we need at least two reviews for this state.
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', '?']);

        self::assertEquals(ReviewState::NEEDS_CLARIFICATION, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_resolution_yes()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'No'], 'Yes');

        self::assertEquals(ReviewState::RESOLVED_YES, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_resolution_no()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'No'], 'No');

        self::assertEquals(ReviewState::RESOLVED_NO, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_resolution_unresolved()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'No'], '?');

        self::assertEquals(ReviewState::UNRESOLVED, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    function test_resolution_is_absolute()
    {
        // Resolution determines the result, even if there are too few reviews and requests for clarification.
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['?', 'Yes'], 'No');

        self::assertEquals(ReviewState::RESOLVED_NO, $misuse->getReviewState($this->container->settings["default_required_reviews"]));
    }

    private function someMisuseWithOneFindingAndReviewDecisions($decisions, $resolutionDecision = null)
    {
        $misuse = Misuse::create(['misuse_muid' => "test", 'run_id' => 1, 'detector_id' => $this->detector->id]);
        $finding = TestHelper::createFindingWith(Experiment::find(2), $this->detector, $misuse);
        $reviewController = new ReviewsController($this->container);
        foreach ($decisions as $index => $decision) {
            $reviewer = Reviewer::firstOrCreate(['name' => 'reviewer' . $index]);
            $this->reviewsControllerHelper->createReview($misuse, $reviewer, $decision);
        }
        if ($resolutionDecision) {
            $this->reviewsControllerHelper->createReview($misuse, Reviewer::firstOrCreate(['name' => 'resolution']), $resolutionDecision);
        }

        return $misuse;
    }
}
