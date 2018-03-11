<?php

use MuBench\ReviewSite\Models\Reviewer;

require_once 'SlimTestCase.php';


class ReviewerTest extends SlimTestCase
{
    public function testGetResolutionReviewer()
    {
        $resolution_reviewer = Reviewer::getResolutionReviewer();

        self::assertEquals('resolution', $resolution_reviewer->name);
    }

    public function testIsResolutionReviewer()
    {
        $resolution_reviewer = Reviewer::where(['name' => 'resolution'])->first();

        self::assertTrue($resolution_reviewer->isResolutionReviewer());
    }

    public function testIsNotResolutionReviewer()
    {
        $reviewer = Reviewer::create(['name' => ':arbitrary:']);

        self::assertFalse($reviewer->isResolutionReviewer());
    }
}
