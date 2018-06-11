<?php

use MuBench\ReviewSite\Controllers\MetadataController;
use MuBench\ReviewSite\Controllers\ReviewsController;
use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Controllers\SnippetsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\Run;
use MuBench\ReviewSite\Models\Snippet;

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

    public function testFindsSnippetForFinding()
    {
        $this->createRunWithFindingInLine(11);

        Snippet::createIfNotExists("-p-", "-v-", "-m-", "//src/file", 10, "m(A){\n\ta(A);\n}");

        $run = Run::of(Detector::find('-d-'))->in(Experiment::find(1))->first();

        self::assertEquals(1, count($run->misuses[0]->snippets()));
        self::assertEquals(10, $run->misuses[0]->snippets()[0]->line);
    }

    public function testFiltersUnrelatedSnippet()
    {
        $this->createRunWithFindingInLine(11);
        $this->createSnippetWithStartLine(9);
        $this->createSnippetWithStartLine(15);

        $run = Run::of(Detector::find('-d-'))->in(Experiment::find(1))->first();

        self::assertEquals(1, count($run->misuses[0]->snippets()));
        self::assertEquals(9, $run->misuses[0]->snippets()[0]->line);
    }

    public function testNoMatchingSnippetsDisplayAll()
    {
        $this->createRunWithFindingInLine(20);
        $this->createSnippetWithStartLine(12);
        $this->createSnippetWithStartLine(9);

        $run = Run::of(Detector::find('-d-'))->in(Experiment::find(1))->first();

        self::assertEquals(2, count($run->misuses[0]->snippets()));
    }

    public function testSnippetsWithFindingWithoutStartLine()
    {
        $runsController = new RunsController($this->container);
        $runsController->addRun(1, '-d-', '-p-', '-v-', [
            "result" => "success",
            "runtime" => 42.1,
            "number_of_findings" => 23,
            "-custom-stat-" => "-stat-val-",
            "timestamp" => 12,
            "potential_hits" => [
                [
                    "misuse" => "-m-",
                    "rank" => 0,
                    "target_snippets" => [
                    ],
                    "file" => "//src/file",
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]]
        ]);
        $this->createSnippetWithStartLine(12);
        $this->createSnippetWithStartLine(9);

        $run = Run::of(Detector::find('-d-'))->in(Experiment::find(1))->first();

        self::assertEquals(2, count($run->misuses[0]->snippets()));
    }

    function testGetAllTagsWhenConclusive()
    {
        $reviewer1 = Reviewer::create(['name' => 'reviewer1']);
        $reviewer2 = Reviewer::create(['name' => 'reviewer2']);

        $this->createRunWithFindingInLine(10);
        $misuse = Misuse::find(1);

        $this->createReview($misuse, $reviewer1, 'Yes', [], ['reviewer1-tag']);
        $this->createReview($misuse, $reviewer2, 'Yes', [], ['reviewer2-tag']);

        self::assertEquals(2, Misuse::find(1)->getTags()->count());
    }

    function testGetTagsOfReviewerWhenNotConclusive()
    {
        $reviewer1 = Reviewer::create(['name' => 'reviewer1']);
        $reviewer2 = Reviewer::create(['name' => 'reviewer2']);

        $this->createRunWithFindingInLine(10);
        $misuse = Misuse::find(1);

        $this->createReview($misuse, $reviewer1, 'Yes', [], ['reviewer1-tag']);
        $this->createReview($misuse, $reviewer2, 'No', [], ['reviewer2-tag']);

        $tags = $misuse->getReview($reviewer1)->tags;
        self::assertEquals(1, $tags->count());
        self::assertEquals('reviewer1-tag', $tags[0]->name);
    }

    function testGetNoTagsWithoutReviewerWhenNotConclusive()
    {
        $reviewer1 = Reviewer::create(['name' => 'reviewer1']);
        $this->createRunWithFindingInLine(10);
        $misuse = Misuse::find(1);

        $this->createReview($misuse, $reviewer1, 'Yes', [], ['reviewer1-tag']);

        self::assertEquals(0, $misuse->getTags()->count());
    }

    public function createRunWithFindingInLine($line)
    {
        $runsController = new RunsController($this->container);
        $runsController->addRun(1, '-d-', '-p-', '-v-', [
            "result" => "success",
            "runtime" => 42.1,
            "number_of_findings" => 23,
            "-custom-stat-" => "-stat-val-",
            "timestamp" => 12,
            "potential_hits" => [
                [
                    "misuse" => "-m-",
                    "rank" => 0,
                    "target_snippets" => [
                    ],
                    "file" => "//src/file",
                    "startline" => $line,
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]]
        ]);
    }

    public function createSnippetWithStartLine($line){
        Snippet::createIfNotExists("-p-", "-v-", "-m-", "//src/file", $line, "m(A){\n\ta(A);\n}");
    }
}
