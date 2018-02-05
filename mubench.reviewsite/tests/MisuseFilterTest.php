<?php

namespace MuBench\ReviewSite\Controllers;

require_once 'SlimTestCase.php';

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Reviewer;
use SlimTestCase;

class MisuseFilterTest extends SlimTestCase
{
    /** @var ReviewsController */
    private $reviewController;
    /** @var RunsController */
    private $runController;
    /** @var Experiment */
    private $experiment;
    /** @var Detector */
    private $detector;
    /** @var Reviewer */
    private $reviewer1;
    /** @var Reviewer */
    private $reviewer2;

    private $undecided_review = [
        'hit' => '?',
        'types' => []
    ];

    private $decided_review = [
        'hit' => 'Yes',
        'types' => []
    ];

    function setUp()
    {
        parent::setUp();

        $this->reviewer1 = Reviewer::create(['name' => 'test-reviewer1']);
        $this->reviewer2 = Reviewer::create(['name' => 'test-reviewer2']);
        $this->experiment = Experiment::find(2);
        $this->detector = Detector::create(['muid' => 'test-detector']);

        $this->runController = new RunsController($this->container);
        $this->reviewController = new ReviewsController($this->container);

        $this->runController->addRun(
            $this->experiment->id,
            $this->detector->muid,
            '-project-muid-',
            '-version-muid-',
            (object) [
                'timestamp' => 1337,
                'result' => 'success',
                'runtime' => 42.0,
                'number_of_findings' => 3,
                'potential_hits' => [
                    (object) ['misuse' => '1', 'rank' => 1, 'file' => '-foo.java-', 'target_snippets' => []],
                    (object) ['misuse' => '2', 'rank' => 2, 'file' => '-foo.java-', 'target_snippets' => []]
                ]
            ]);
    }

    function test_counts_misuse_without_reviews()
    {
        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1);

        self::assertEquals(1, sizeof($runs[0]->misuses));
    }

    function test_counts_misuse_with_single_conclusive_review()
    {
        $this->reviewController->updateOrCreateReview('1', $this->reviewer1->id, '', [1 => $this->decided_review]);

        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1);

        self::assertEquals(1, sizeof($runs[0]->misuses));
    }

    function test_counts_misuse_with_multiple_conclusive_reviews()
    {
        $this->reviewController->updateOrCreateReview('1', $this->reviewer1->id, '', [1 => $this->decided_review]);
        $this->reviewController->updateOrCreateReview('1', $this->reviewer2->id, '', [1 => $this->decided_review]);

        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1);

        self::assertEquals(1, sizeof($runs[0]->misuses));
    }

    function test_ignores_misuse_with_single_inconclusive_review()
    {
        $this->reviewController->updateOrCreateReview('1', $this->reviewer1->id, '', [1 => $this->undecided_review]);

        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1);

        self::assertEquals(2, sizeof($runs[0]->misuses));
    }

    function test_ignores_misuse_with_at_least_one_inconclusive_review()
    {
        $this->reviewController->updateOrCreateReview('1', $this->reviewer1->id, '', [1 => $this->undecided_review]);
        $this->reviewController->updateOrCreateReview('1', $this->reviewer2->id, '', [1 => $this->decided_review]);

        $runs = $this->runController->getRuns($this->detector, $this->experiment, 1);

        self::assertEquals(2, sizeof($runs[0]->misuses));
    }
}
