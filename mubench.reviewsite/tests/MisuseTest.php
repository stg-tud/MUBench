<?php

namespace MuBench\ReviewSite\Tests;

use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\Run;
use MuBench\ReviewSite\Models\Snippet;

class MisuseTest extends SlimTestCase
{

    /** @var ReviewsControllerHelper */
    private $reviewsControllerHelper;

    private $FINDING_SRC_FILE = "//src/file";

    public function setUp()
    {
        parent::setUp();
        $this->reviewsControllerHelper = new ReviewsControllerHelper($this->container);
    }

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
        $finding = $this->createMisuseWithFinding(11);
        $snippet = $this->createThreeLineSnippet($finding, 10);

        self::assertCount(1, $finding->snippets());
        self::assertEquals($snippet->id, $finding->snippets()[0]->id);
    }

    public function testFiltersUnrelatedSnippetByLine()
    {
        $finding = $this->createMisuseWithFinding(11);
        $snippet = $this->createThreeLineSnippet($finding, 9);
        $this->createThreeLineSnippet($finding, 15);

        self::assertCount(1, $finding->snippets());
        self::assertEquals($snippet->id, $finding->snippets()[0]->id);
    }

    public function testFiltersUnrelatedSnippetsWithoutStartLine()
    {
        $finding = $this->createMisuseWithFinding(null);
        $this->createThreeLineSnippet($finding, 1337);
        Snippet::createIfNotExists('-otherProject-', '-v-', '-m-', '//other/file', 42, 'foo(){}');

        self::assertCount(1, $finding->snippets());
    }

    public function testReturnsAllSnippetsIfNoneMatchByLine()
    {
        $finding = $this->createMisuseWithFinding(20);
        $this->createThreeLineSnippet($finding, 12);
        $this->createThreeLineSnippet($finding, 9);

        self::assertCount(2, $finding->snippets());
    }

    function testGetAllTagsWhenConclusive()
    {
        $reviewer1 = Reviewer::create(['name' => 'reviewer1']);
        $reviewer2 = Reviewer::create(['name' => 'reviewer2']);
        $misuse = $this->createMisuseWithFinding(10);

        $this->reviewsControllerHelper->createReview($misuse, $reviewer1, 'Yes', [], ['reviewer1-tag']);
        $this->reviewsControllerHelper->createReview($misuse, $reviewer2, 'Yes', [], ['reviewer2-tag']);

        self::assertCount(2, $misuse->getTags($this->container->settings["number_of_required_reviews"]));
    }

    function testGetTagsOfReviewerWhenNotConclusive()
    {
        $reviewer1 = Reviewer::create(['name' => 'reviewer1']);
        $reviewer2 = Reviewer::create(['name' => 'reviewer2']);
        $misuse = $this->createMisuseWithFinding(10);

        $this->reviewsControllerHelper->createReview($misuse, $reviewer1, 'Yes', [], ['reviewer1-tag']);
        $this->reviewsControllerHelper->createReview($misuse, $reviewer2, 'No', [], ['reviewer2-tag']);

        $tags = $misuse->getReview($reviewer1)->tags;
        self::assertCount(1, $tags);
        self::assertEquals('reviewer1-tag', $tags[0]->name);
    }

    function testGetNoTagsWithoutReviewerWhenNotConclusive()
    {
        $reviewer1 = Reviewer::create(['name' => 'reviewer1']);
        $misuse = $this->createMisuseWithFinding(10);

        $this->reviewsControllerHelper->createReview($misuse, $reviewer1, 'Yes', [], ['reviewer1-tag']);

        self::assertEmpty($misuse->getTags($this->container->settings["number_of_required_reviews"]));
    }

    /**
     * @param int $startLine
     * @return Misuse
     */
    public function createMisuseWithFinding($startLine = null)
    {
        $experimentId = 1;
        $detectorId = '-d-';
        $projectId = '-p-';
        $versionId = '-v-';
        $runsController = new RunsController($this->container);
        $runsController->addRun($experimentId, $detectorId, $projectId, $versionId, [
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
                    "file" => $this->FINDING_SRC_FILE,
                    "startline" => $startLine,
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]]
        ]);
        return Run::of(Detector::find($detectorId))->in(Experiment::find($experimentId))
            ->where('project_muid', $projectId)->where('version_muid', $versionId)->first()->misuses[0];
    }

    private function createThreeLineSnippet(Misuse $misuse, $line)
    {
        return Snippet::createIfNotExists($misuse->getProject(), $misuse->getVersion(), $misuse->misuse_muid,
            $this->FINDING_SRC_FILE, $line, "m(A){\n\ta(A);\n}");
    }
}
