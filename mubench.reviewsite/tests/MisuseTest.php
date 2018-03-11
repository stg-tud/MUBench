<?php

use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\Reviewer;

require_once 'SlimTestCase.php';


class MisuseTest extends SlimTestCase
{
    public function testHasReviewed()
    {
        $reviewer = Reviewer::create(['name' => ':arbitrary:']);
        $misuse = Misuse::create(['run_id' => 42, 'detector_id' => 42, 'misuse_muid' => ':arbitrary:']);
        $review = Review::create(['misuse_id' => $misuse->id, 'reviewer_id' => $reviewer->id, 'comment' => ':none:']);

        self::assertTrue($misuse->hasReviewed($reviewer));
    }

    public function testGetResolutionReview()
    {
        $resolution_reviewer = Reviewer::where(['name' => 'resolution'])->first();
        $misuse = Misuse::create(['run_id' => 42, 'detector_id' => 42, 'misuse_muid' => ':arbitrary:']);
        $review = Review::create(['misuse_id' => $misuse->id, 'reviewer_id' => $resolution_reviewer->id, 'comment' => ':none:']);

        self::assertTrue($misuse->hasResolutionReview());
        self::assertEquals($review->id, $misuse->getResolutionReview()->id);
    }

    public function testNoResolutionReview()
    {
        $misuse = Misuse::create(['run_id' => 42, 'detector_id' => 42, 'misuse_muid' => ':arbitrary:']);

        self::assertFalse($misuse->hasResolutionReview());
    }
}
