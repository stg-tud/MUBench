<?php

namespace MuBench\ReviewSite\Controller;

require_once 'DatabaseTestCase.php';

use DatabaseTestCase;
use MuBench\ReviewSite\Model\Decision;
use MuBench\ReviewSite\Model\Review;
use Slim\Views\PhpRenderer;

class StoreReviewTest extends DatabaseTestCase
{
    private $detector;

    /**
     * @var ReviewController $reviewController
     */
    private $reviewController;

    function setUp()
    {
        parent::setUp();
        $this->detector = $this->db->getOrCreateDetector('-d-');
        $this->reviewController = new ReviewController('', '', $this->db, new PhpRenderer());
    }


    function test_store_review()
    {
        $this->reviewController->updateReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-', '-comment-', [['hit' => 'Yes']]);

        $review = $this->reviewController->getReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-');

        self::assertEquals(new Review([
            'name' => '-reviewer-',
            'exp' => 'ex1',
            'detector' => $this->detector->id,
            'project' => '-p-',
            'version' => '-v-',
            'misuse' => '-m-',
            'comment' => '-comment-',
            'id' => '1',
            'finding_reviews' => [
                [
                    'decision' => 'Yes',
                    'id' => '1',
                    'rank' => '0',
                    'review' => '1',
                    'violation_types' => []
                ]
            ]
        ]), $review);
    }

    function test_update_review()
    {
        $this->reviewController->updateReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-', '-comment-', [['hit' => 'Yes']]);
        $this->reviewController->updateReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-', '-comment-', [['hit' => 'No']]);

        $review = $this->reviewController->getReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-');

        $decision = $review->getDecision();
        self::assertEquals(Decision::NO, $decision);
    }

    function test_stores_violation_types()
    {
        $this->reviewController->updateReview('ex2', $this->detector, '-p-', '-v-', '-m-', '-reviewer-', '-comment-', [['hit' => 'Yes', 'types' => ['1']]]);

        $review = $this->reviewController->getReview('ex2', $this->detector, '-p-', '-v-', '-m-', '-reviewer-');

        $actualTypes = $review->getHitViolationTypes(0);
        self::assertEquals(["missing/call"], $actualTypes);
    }
}
