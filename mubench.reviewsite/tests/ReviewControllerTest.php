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
        Misuse::create(['misuse_muid' => '0', 'run_id' => 1, 'detector_id' => 42]);
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

}
