<?php

use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\Review;
use MuBench\ReviewSite\Model\ReviewState;

class ReviewStateTest extends \PHPUnit\Framework\TestCase
{
    function test_no_potential_hits()
    {
        $misuse = new Misuse(["misuse" => "test"], [], []);

        self::assertEquals(ReviewState::NOTHING_TO_REVIEW, $misuse->getReviewState());
    }

    function test_needs_2_reviews()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], []);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_needs_1_review()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]])
        ]);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_needs_review_overrules_needs_carification()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "?"]]])
        ]);

        self::assertEquals(ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_agreement_yes()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]]),
            new Review(["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "Yes"]]])
        ]);

        self::assertEquals(ReviewState::AGREEMENT_YES, $misuse->getReviewState());
    }

    function test_agreement_no()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "No"]]]),
            new Review(["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]])
        ]);

        self::assertEquals(ReviewState::AGREEMENT_NO, $misuse->getReviewState());
    }

    function test_disagreement()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]]),
            new Review(["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]])
        ]);

        self::assertEquals(ReviewState::DISAGREEMENT, $misuse->getReviewState());
    }

    function test_needs_clarification()
    {
        // NEEDS_REVIEW takes precedence over NEEDS_CLARIFICATION, hence, we need at least two reviews for this state.
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "?"]]]),
            new Review(["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "Yes"]]])
        ]);

        self::assertEquals(ReviewState::NEEDS_CLARIFICATION, $misuse->getReviewState());
    }

    function test_resolution_yes()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]]),
            new Review(["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]]),
            new Review(["name" => "resolution", "finding_reviews" => ["0" => ["decision" => "Yes"]]])
        ]);

        self::assertEquals(ReviewState::RESOLVED_YES, $misuse->getReviewState());
    }

    function test_resolution_no()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]]),
            new Review(["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]]),
            new Review(["name" => "resolution", "finding_reviews" => ["0" => ["decision" => "No"]]])
        ]);

        self::assertEquals(ReviewState::RESOLVED_NO, $misuse->getReviewState());
    }

    function test_resolution_unresolved()
    {
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]]),
            new Review(["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]]),
            new Review(["name" => "resolution", "finding_reviews" => ["0" => ["decision" => "?"]]])
        ]);

        self::assertEquals(ReviewState::UNRESOLVED, $misuse->getReviewState());
    }

    function test_resolution_is_absolute()
    {
        // Resolution determines the result, even if there are too few reviews and requests for clarification.
        $misuse = new Misuse(["misuse" => "test"], [["rank" => "0"]], [
            new Review(["name" => "sven", "finding_reviews" => ["0" => ["decision" => "?"]]]),
            new Review(["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "Yes"]]]),
            new Review(["name" => "resolution", "finding_reviews" => ["0" => ["decision" => "No"]]])
        ]);

        self::assertEquals(ReviewState::RESOLVED_NO, $misuse->getReviewState());
    }
}
