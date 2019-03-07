<?php

namespace MuBench\ReviewSite\Tests;

use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Reviewer;

class MisuseFilterTest extends SlimTestCase
{
    /** @var RunsController */
    private $runController;
    /** @var ReviewsControllerHelper */
    private $reviewControllerHelper;
    /** @var Experiment */
    private $experiment;
    /** @var Detector */
    private $detector;
    /** @var Reviewer */
    private $reviewer1;
    /** @var Reviewer */
    private $reviewer2;
    /** @var Misuse */
    private $misuse;

    function setUp()
    {
        parent::setUp();

        $this->reviewer1 = Reviewer::create(['name' => 'test-reviewer1']);
        $this->reviewer2 = Reviewer::create(['name' => 'test-reviewer2']);
        $this->experiment = Experiment::find(2);
        $this->detector = Detector::create(['muid' => 'test-detector']);

        $this->runController = new RunsController($this->container);
        $this->reviewControllerHelper = new ReviewsControllerHelper($this->container);

        $this->runController->addRun(
            $this->experiment->id,
            $this->detector->muid,
            '-project-muid-',
            '-version-muid-',
            [
                'timestamp' => 1337,
                'result' => 'success',
                'runtime' => 42.0,
                'number_of_findings' => 3,
                'potential_hits' => [
                    ['misuse' => '1', 'rank' => 1, 'file' => '-foo.java-', 'target_snippets' => []],
                    ['misuse' => '2', 'rank' => 2, 'file' => '-foo.java-', 'target_snippets' => []]
                ]
            ]);
        $this->misuse = Misuse::find(1);
    }

    function test_counts_misuse_without_reviews()
    {
        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1, 2);

        self::assertEquals(1, sizeof($runs[0]->misuses));
    }

    function test_counts_misuse_with_single_conclusive_review()
    {
        $this->reviewControllerHelper->createReview($this->misuse, $this->reviewer1, 'Yes');

        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1, 2);

        self::assertEquals(1, sizeof($runs[0]->misuses));
    }

    function test_counts_misuse_with_multiple_conclusive_reviews()
    {
        $this->reviewControllerHelper->createReview($this->misuse, $this->reviewer1, 'Yes');
        $this->reviewControllerHelper->createReview($this->misuse, $this->reviewer2, 'Yes');

        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1, 2);

        self::assertEquals(1, sizeof($runs[0]->misuses));
    }

    function test_ignores_misuse_with_single_inconclusive_review()
    {
        $this->reviewControllerHelper->createReview($this->misuse, $this->reviewer1, '?');

        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1, 2);

        self::assertEquals(2, sizeof($runs[0]->misuses));
    }

    function test_ignores_misuse_with_at_least_one_inconclusive_review()
    {
        $this->reviewControllerHelper->createReview($this->misuse, $this->reviewer1, '?');
        $this->reviewControllerHelper->createReview($this->misuse, $this->reviewer2, 'Yes');

        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1, 2);

        self::assertEquals(2, sizeof($runs[0]->misuses));
    }
}
