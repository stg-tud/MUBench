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
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [["name" => "sven"]]);

        self::assertEquals(\MuBench\ReviewState::NEEDS_REVIEW, $misuse->getReviewState());
    }

    function test_agreement()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]],
            ["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "Yes"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::AGREEMENT, $misuse->getReviewState());
    }

    function test_disagreement()
    {
        $misuse = new \MuBench\Misuse(["misuse" => "test"], [["rank" => "0"]], [
            ["name" => "sven", "finding_reviews" => ["0" => ["decision" => "Yes"]]],
            ["name" => "hoan", "finding_reviews" => ["0" => ["decision" => "No"]]]
        ]);

        self::assertEquals(\MuBench\ReviewState::DISAGREEMENT, $misuse->getReviewState());
    }
}
