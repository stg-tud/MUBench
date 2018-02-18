<?php

namespace MuBench\ReviewSite\Controllers;

require_once 'SlimTestCase.php';

use MuBench\ReviewSite\Models\Decision;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\Type;
use SlimTestCase;

class ReviewControllerTest extends SlimTestCase
{
    /**
     * @var ReviewsController $reviewController
     */
    private $reviewController;

    /**
     * @var Reviewer $reviewer1
     */
    private $reviewer1;

    /**
     * @var Reviewer $reviewer2
     */
    private $reviewer2;

    function setUp()
    {
        parent::setUp();
        $this->reviewController = new ReviewsController($this->container);
        $this->reviewer1 = Reviewer::create(['name' => 'reviewer1']);
        $this->reviewer2 = Reviewer::create(['name' => 'reviewer2']);
    }


    function test_store_review()
    {
        Misuse::create(['misuse_muid' => '0', 'run_id' => 2, 'detector_id' => 1]);

        $this->reviewController->updateOrCreateReview(1, $this->reviewer1->id, '-comment-', [['hit' => 'Yes', 'types' => []]]);

        $review = Misuse::find(1)->getReview($this->reviewer1);
        self::assertEquals('-comment-', $review->comment);
        self::assertEquals(Decision::YES, $review->getDecision());
    }

    function test_update_review()
    {
        Misuse::create(['misuse_muid' => '0', 'run_id' => 2, 'detector_id' => 1]);

        $this->reviewController->updateOrCreateReview(1, $this->reviewer1->id, '-comment-', [['hit' => 'Yes', 'types' => []]]);
        $this->reviewController->updateOrCreateReview(1, $this->reviewer1->id, '-comment-', [['hit' => 'No', 'types' => []]]);

        $review = Misuse::find(1)->getReview($this->reviewer1);
        self::assertEquals('-comment-', $review->comment);
        self::assertEquals(Decision::NO, $review->getDecision());
    }

    function test_stores_violation_types()
    {
        Misuse::create(['misuse_muid' => '0', 'run_id' => 2, 'detector_id' => 1]);
        Type::create(['name' => 'missing/call']);

        $this->reviewController->updateOrCreateReview(1, $this->reviewer1->id, '-comment-', [['hit' => 'No', 'types' => [1]]]);

        $review = Misuse::find(1)->getReview($this->reviewer1);
        $violation_types = $review->getHitViolationTypes('0');
        self::assertEquals("missing/call", $violation_types[0]["name"]);
    }

    function test_determine_next_misuse_current_and_next_are_reviewed()
    {
        $this->createRuWithThreeMisuses();
        list($misuse1, $misuse2, $misuse3) = Misuse::all()->all();

        $this->createConclusiveReviewState($misuse1);
        $this->createConclusiveReviewState($misuse2);

        // current misuse = 1, reviewer = 1
        list($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse)  = $this->reviewController->determineNavigationTargets(Misuse::all(), '-p-', '-v-', $misuse1->misuse_muid, $this->reviewer1);

        self::assertEquals($misuse3->misuse_muid, $previous_misuse->misuse_muid);
        self::assertEquals($misuse2->misuse_muid, $next_misuse->misuse_muid);
        self::assertEquals($misuse3->misuse_muid, $next_reviewable_misuse->misuse_muid);
        self::assertEquals($misuse1->misuse_muid, $misuse->misuse_muid);
    }

    function test_determine_next_misuse_current_is_only_reviewable()
    {
        $this->createRuWithThreeMisuses();
        list($misuse1, $misuse2, $misuse3) = Misuse::all()->all();

        $this->createConclusiveReviewState($misuse1);
        $this->createConclusiveReviewState($misuse2);

        // current misuse = 3, reviewer = 1
        list($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse)  = $this->reviewController->determineNavigationTargets(Misuse::all(), '-p-', '-v-', $misuse3->misuse_muid, $this->reviewer1);

        self::assertEquals($misuse2->misuse_muid, $previous_misuse->misuse_muid);
        self::assertEquals($misuse1->misuse_muid, $next_misuse->misuse_muid);
        self::assertNull($next_reviewable_misuse);
        self::assertEquals($misuse3->misuse_muid, $misuse->misuse_muid);
    }

    function test_determine_next_misuse_not_fully_reviewed()
    {
        $this->createRuWithThreeMisuses();
        list($misuse1, $misuse2, $misuse3) = Misuse::all()->all();

        $this->createReview($misuse1, $this->reviewer2);
        $this->createReview($misuse2, $this->reviewer1);
        $this->createReview($misuse3, $this->reviewer2);

        // current misuse = 1, reviewer = 1
        list($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse)  = $this->reviewController->determineNavigationTargets(Misuse::all(), '-p-', '-v-', $misuse1->misuse_muid, $this->reviewer1);

        self::assertEquals($misuse3->misuse_muid, $previous_misuse->misuse_muid);
        self::assertEquals($misuse2->misuse_muid, $next_misuse->misuse_muid);
        self::assertEquals($misuse3->misuse_muid, $next_reviewable_misuse->misuse_muid);
        self::assertEquals($misuse1->misuse_muid, $misuse->misuse_muid);
    }

    private function createRuWithThreeMisuses()
    {
        $runsController = new RunsController($this->container);
        $runsController->addRun(1, 'test-detector', '-p-', '-v-',json_decode(json_encode(
            [
                "result" => "success",
                "runtime" => 42.1,
                "number_of_findings" => 23,
                "timestamp" => 12,
                "potential_hits" => [
                    [
                        "misuse" => "0",
                        "rank" => 0,
                    ],
                    [
                        "misuse" => "1",
                        "rank" => 0,
                    ],
                    [
                        "misuse" => "2",
                        "rank" => 0,
                    ]
                ]
            ]
        )));
    }

    private function createConclusiveReviewState($misuse)
    {
        $this->createReview($misuse, $this->reviewer1);
        $this->createReview($misuse, $this->reviewer2);
    }

    private function createReview($misuse, $reviewer)
    {
        $this->reviewController->updateOrCreateReview($misuse->id, $reviewer->id, '-comment-', [['hit' => 'No', 'types' => [1]]]);
    }

}
