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

    function test_find_reviewer_by_id()
    {
        $expectedReviewer = Reviewer::create(['name' => '-reviewer-']);
        $reviewer = Reviewer::findByIdOrName($expectedReviewer->id);

        self::assertEquals($expectedReviewer->id, $reviewer->id);
        self::assertEquals($expectedReviewer->name, $reviewer->name);
    }

    function test_find_reviewer_by_name()
    {
        $expectedReviewer = Reviewer::create(['name' => '-reviewer-']);
        $reviewer = Reviewer::findByIdOrName('-reviewer-');

        self::assertEquals($expectedReviewer->id, $reviewer->id);
        self::assertEquals($expectedReviewer->name, $reviewer->name);
    }
}
