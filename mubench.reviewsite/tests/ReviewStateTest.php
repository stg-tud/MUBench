<?php

use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\Review;
use MuBench\ReviewSite\Model\ReviewState;

class ReviewStateTest extends \PHPUnit\Framework\TestCase
{
    function test_no_potential_hits()
    {
        $misuse = new Misuse(["misuse" => "test"], [], [], []);

        self::assertEquals(ReviewState::NOTHING_TO_REVIEW, $misuse->getReviewState());
    }

    function test_needs_2_reviews()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions([/* none */]);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_needs_1_review()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes']);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_needs_review_overrules_needs_carification()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['?']);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_agreement_yes()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'Yes']);

        self::assertEquals(ReviewState::AGREEMENT_YES, $misuse->getReviewState());
    }

    function test_agreement_no()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['No', 'No']);

        self::assertEquals(ReviewState::AGREEMENT_NO, $misuse->getReviewState());
    }

    function test_disagreement()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'No']);

        self::assertEquals(ReviewState::DISAGREEMENT, $misuse->getReviewState());
    }

    function test_needs_clarification()
    {
        // NEEDS_REVIEW takes precedence over NEEDS_CLARIFICATION, hence, we need at least two reviews for this state.
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', '?']);

        self::assertEquals(ReviewState::NEEDS_CLARIFICATION, $misuse->getReviewState());
    }

    function test_resolution_yes()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'No'], 'Yes');

        self::assertEquals(ReviewState::RESOLVED_YES, $misuse->getReviewState());
    }

    function test_resolution_no()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'No'], 'No');

        self::assertEquals(ReviewState::RESOLVED_NO, $misuse->getReviewState());
    }

    function test_resolution_unresolved()
    {
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['Yes', 'No'], '?');

        self::assertEquals(ReviewState::UNRESOLVED, $misuse->getReviewState());
    }

    function test_resolution_is_absolute()
    {
        // Resolution determines the result, even if there are too few reviews and requests for clarification.
        $misuse = $this->someMisuseWithOneFindingAndReviewDecisions(['?', 'Yes'], 'No');

        self::assertEquals(ReviewState::RESOLVED_NO, $misuse->getReviewState());
    }

    private function someMisuseWithOneFindingAndReviewDecisions($decisions, $resolutionDecision = null)
    {
        $findingRank = '0';

        $reviews = [];
        foreach ($decisions as $index => $decision) {
            $reviews[] = new Review([
                'name' => 'reviewer_' . $index,
                'finding_reviews' => [$findingRank => ['decision' => $decision]]
            ]);
        }

        if ($resolutionDecision) {
            $reviews[] = new Review([
                'name' => 'resolution',
                'finding_reviews' => [$findingRank => ['decision' => $resolutionDecision]]
            ]);
        }

        return new Misuse(['misuse' => 'test'], [['rank' => $findingRank]], $reviews, []);
    }
}
