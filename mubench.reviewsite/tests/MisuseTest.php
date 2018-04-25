<?php

use MuBench\ReviewSite\Controllers\MetadataController;
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

    public function testCheckSnippetsWithFindings()
    {
        $this->createRunWithFinding(11);

        SnippetsController::createSnippetIfNotExists("-p-", "-v-", "-m-", "//src/file", 10, "m(A){\n\ta(A);\n}");

        $run = Run::of(Detector::find('-d-'))->in(Experiment::find(1))->first();

        self::assertEquals(1, $run->misuses->count());
        self::assertEquals(1, count($run->misuses[0]->snippets()));
        self::assertEquals(10, $run->misuses[0]->snippets()[0]->line);
    }

    public function testCheckSnippetsWithMetadataAndFindings()
    {
        $this->createRunWithFinding(10);

        $metadataController = new MetadataController($this->container);
        $metadataController->putMetadataCollection([[
            'project' => '-p-',
            'version' => '-v-',
            'misuse' => '-m-',
            'description' => '-desc-',
            'fix' => ['diff-url' => '-diff-', 'description' => '-fix-desc-'],
            'location' => ['file' => '//src/file', 'method' => '-method-location-', 'line' => 11],
            'violations' => ['missing/call'],
            'correct_usages' => [['id' => '-p1-', 'snippet' => ['code' => '-code-', 'first_line' => 42]]],
            'target_snippets' => [['code' => "m(A){\n\ta(A);\n}", 'first_line_number' => 10]]
        ]]);
        $this->createSnippetWithStartLine(15);
        $this->createSnippetWithStartLine(8);

        $run = Run::of(Detector::find('-d-'))->in(Experiment::find(1))->first();
        $snippets = Snippet::all();
        self::assertEquals(1, $run->misuses->count());
        self::assertEquals(2, count($run->misuses[0]->snippets()));
        self::assertEquals(8, $run->misuses[0]->snippets()[0]->line);
        self::assertEquals(10, $run->misuses[0]->snippets()[1]->line);
    }

    public function createRunWithFinding($line)
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
        SnippetsController::createSnippetIfNotExists("-p-", "-v-", "-m-", "//src/file", $line, "m(A){\n\ta(A);\n}");
    }
}
