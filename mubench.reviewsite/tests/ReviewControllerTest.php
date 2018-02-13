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

    function setUp()
    {
        parent::setUp();
        $this->reviewController = new ReviewsController($this->container);
        Misuse::create(['misuse_muid' => '0', 'run_id' => 1, 'detector_id' => 1]);
        Reviewer::create(['name' => 'reviewer1']);
    }


    function test_store_review()
    {
        $this->reviewController->updateOrCreateReview(1, 1, '-comment-', [['hit' => 'Yes', 'types' => []]]);
        $review = Misuse::find(1)->getReview(Reviewer::find(1));
        self::assertEquals('-comment-', $review->comment);
        self::assertEquals(Decision::YES, $review->getDecision());
    }

    function test_update_review()
    {
        $this->reviewController->updateOrCreateReview(1, 1, '-comment-', [['hit' => 'Yes', 'types' => []]]);
        $this->reviewController->updateOrCreateReview(1, 1, '-comment-', [['hit' => 'No', 'types' => []]]);

        $review = Misuse::find(1)->getReview(Reviewer::find(1));
        self::assertEquals('-comment-', $review->comment);
        self::assertEquals(Decision::NO, $review->getDecision());
    }

    function test_stores_violation_types()
    {
        Type::create(['name' => 'missing/call']);
        $this->reviewController->updateOrCreateReview(1, 1, '-comment-', [['hit' => 'No', 'types' => [1]]]);

        $review = Misuse::find(1)->getReview(Reviewer::find(1));
        $violation_types = $review->getHitViolationTypes('0');
        self::assertEquals("missing/call", $violation_types[0]["name"]);
    }

    function test_determine_next_misuse()
    {
        $this->setupSomeRunWithThreeMisusesAndTwoReviews();

        list($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse)  = $this->reviewController->determineNavigationTargets(Misuse::all(), '-p-', '-v-', '0', Reviewer::find(1));
        self::assertEquals('2', $previous_misuse->misuse_muid);
        self::assertEquals('1', $next_misuse->misuse_muid);
        self::assertEquals('2', $next_reviewable_misuse->misuse_muid);
        self::assertEquals('0', $misuse->misuse_muid);
    }

    function test_determine_next_is_previous_misuse()
    {
        $this->setupSomeRunWithThreeMisusesAndTwoReviews();

        list($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse)  = $this->reviewController->determineNavigationTargets(Misuse::all(), '-p-', '-v-', '2', Reviewer::find(1));
        self::assertEquals('1', $previous_misuse->misuse_muid);
        self::assertEquals('1', $next_misuse->misuse_muid);
        self::assertNull($next_reviewable_misuse);
        self::assertEquals('2', $misuse->misuse_muid);
    }

    private function setupSomeRunWithThreeMisusesAndTwoReviews()
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
        Misuse::create(['misuse_muid' => '1', 'run_id' => 1, 'detector_id' => 1]);
        Misuse::create(['misuse_muid' => '2', 'run_id' => 1, 'detector_id' => 1]);
        Reviewer::create(['name' => 'reviewer2']);
        $this->reviewController->updateOrCreateReview(1, 1, '-comment-', [['hit' => 'No', 'types' => [1]]]);
        $this->reviewController->updateOrCreateReview(1, 2, '-comment-', [['hit' => 'No', 'types' => [1]]]);
        $this->reviewController->updateOrCreateReview(2, 1, '-comment-', [['hit' => 'No', 'types' => [1]]]);
        $this->reviewController->updateOrCreateReview(2, 2, '-comment-', [['hit' => 'No', 'types' => [1]]]);
    }

}
