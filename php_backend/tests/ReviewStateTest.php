<?php

require_once "src/MuBench/Misuse.php";

class ReviewStateTest extends \PHPUnit\Framework\TestCase
{
    function test_no_potential_hits()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [], []);

        self::assertEquals(\MuBench\ReviewState::NOTHING_TO_REVIEW, $misuse->getReviewState());
    }

    function test_needs_2_reviews()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], []);

        self::assertEquals(\MuBench\ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_needs_1_review()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_needs_review_overrules_needs_carification()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "?"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_agreement_yes()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]],
            ["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "Yes"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::AGREEMENT_YES, $misuse->getReviewState());
    }

    function test_agreement_no()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "No"]]],
            ["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::AGREEMENT_NO, $misuse->getReviewState());
    }

    function test_disagreement()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]],
            ["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::DISAGREEMENT, $misuse->getReviewState());
    }

    function test_needs_clarification()
    {
        // NEEDS_REVIEW takes precedence over NEEDS_CLARIFICATION, hence, we need at least two reviews for this state.
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "?"]]],
            ["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "Yes"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::NEEDS_CLARIFICATION, $misuse->getReviewState());
    }

    function test_resolution_yes()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]],
            ["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]],
            ["name" => "resolution", "finding_reviews" => ["0" => ["decision" => "Yes"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::RESOLVED_YES, $misuse->getReviewState());
    }

    function test_resolution_no()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]],
            ["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]],
            ["name" => "resolution", "finding_reviews" => ["0" => ["decision" => "No"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::RESOLVED_NO, $misuse->getReviewState());
    }

    function test_resolution_is_absolute()
    {
        // Resolution determines the result, even if there are too few reviews and requests for clarification.
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "?"]]],
            ["name" => "resolution", "finding_reviews" => ["0" => ["decision" => "No"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::RESOLVED_NO, $misuse->getReviewState());
    }
}
