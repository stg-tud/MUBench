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

    private $undecided_review = [
        'reviewer_id' => 1,
        'misuse_id' => 1,
        'review_comment' => '-comment-',
        'review_hit' => [
            1 => [
                'hit' => '?',
                'types' => [
                    'missing/call'
                ]
            ]
        ]
    ];

    private $decided_review = [
        'reviewer_id' => 2,
        'misuse_id' => 1,
        'review_comment' => '-comment-',
        'review_hit' => [
            1 => [
                'hit' => 'Yes',
                'types' => [
                    'missing/call'
                ]
            ]
        ]
    ];

    function setUp()
    {
        parent::setUp();
        $this->reviewController = new ReviewsController($this->container);
        $this->runController = new RunsController($this->container);
        $this->detector = Detector::create(['muid' => 'test-detector']);
        Reviewer::create(['name' => 'test-reviewer1']);
        Reviewer::create(['name' => 'test-reviewer2']);
        $this->experiment = Experiment::find(2);
        $run = new \MuBench\ReviewSite\Models\Run;
        $run->setDetector($this->detector);
        Schema::dropIfExists($run->getTable());
        Schema::create($run->getTable(), function (Blueprint $table) {
            $table->increments('id');
            $table->integer('experiment_id');
            $table->string('project_muid', 30);
            $table->string('version_muid', 30);
            $table->float('runtime');
            $table->integer('number_of_findings');
            $table->string('result', 30);
            $table->text('additional_stat')->nullable();
            $table->dateTime('created_at');
            $table->dateTime('updated_at');
        });
        $run->experiment_id = $this->experiment->id;
        $run->project_muid = 'mubench';
        $run->version_muid = '42';
        $run->result = 'success';
        $run->number_of_findings = 2;
        $run->runtime = 3.40;
        $run->save();
        $misuse = new \MuBench\ReviewSite\Models\Misuse;
        $misuse->misuse_muid = '1';
        $misuse->detector_muid = 'test-detector';
        $misuse->run_id = 1;
        $misuse->save();
        $misuse = new \MuBench\ReviewSite\Models\Misuse;
        $misuse->misuse_muid = '2';
        $misuse->detector_muid = 'test-detector';
        $misuse->run_id = 1;
        $misuse->save();
        $misuse = new \MuBench\ReviewSite\Models\Misuse;
        $misuse->misuse_muid = '3';
        $misuse->detector_muid = 'test-detector';
        $misuse->run_id = 1;
        $misuse->save();
        $finding = new \MuBench\ReviewSite\Models\Finding;
        $finding->setDetector($this->detector);
        Schema::dropIfExists($finding->getTable());
        Schema::create($finding->getTable(), function (Blueprint $table) {
            $table->increments('id');
            $table->integer('experiment_id');
            $table->integer('misuse_id');
            $table->string('project_muid', 30);
            $table->string('version_muid', 30);
            $table->string('misuse_muid', 30);
            $table->integer('startline');
            $table->integer('rank');
            $table->integer('additional_column')->nullable();
            $table->text('file');
            $table->text('method');
            $table->dateTime('created_at');
            $table->dateTime('updated_at');
        });
        $finding->experiment_id = $this->experiment->id;
        $finding->misuse_id = 1;
        $finding->project_muid = 'mubench';
        $finding->version_muid = '42';
        $finding->misuse_muid = '1';
        $finding->startline = 113;
        $finding->rank = 1;
        $finding->additional_column = 'test_column';
        $finding->file = 'Test.java';
        $finding->method = "method(A)";
        $finding->save();
        $finding = new \MuBench\ReviewSite\Models\Finding;
        $finding->setDetector($this->detector);
        $finding->experiment_id = $this->experiment->id;
        $finding->misuse_id = 2;
        $finding->project_muid = 'mubench';
        $finding->version_muid = '42';
        $finding->misuse_muid = '2';
        $finding->startline = 113;
        $finding->rank = 1;
        $finding->additional_column = 'test_column';
        $finding->file = 'Test.java';
        $finding->method = "method(A)";
        $finding->save();
        $finding = new \MuBench\ReviewSite\Models\Finding;
        $finding->setDetector($this->detector);
        $finding->experiment_id = $this->experiment->id;
        $finding->misuse_id = 3;
        $finding->project_muid = 'mubench';
        $finding->version_muid = '42';
        $finding->misuse_muid = '3';
        $finding->startline = 113;
        $finding->rank = 1;
        $finding->additional_column = 'test_column';
        $finding->file = 'Test.java';
        $finding->method = "method(A)";
        $finding->save();
    }

    function test_inconclusive_reviews()
    {
        $this->reviewController->updateOrCreateReview($this->decided_review['misuse_id'], $this->decided_review['reviewer_id'], $this->decided_review['review_comment'], $this->decided_review['review_hit']);
        $this->reviewController->updateOrCreateReview($this->undecided_review['misuse_id'], $this->undecided_review['reviewer_id'], $this->undecided_review['review_comment'], $this->undecided_review['review_hit']);
        $runs = $this->runController->getRuns($this->detector, $this->experiment, 2);
        self::assertEquals(3, sizeof($runs[0]->misuses));
    }

    function test_conclusive_reviews()
    {
        $this->reviewController->updateOrCreateReview($this->decided_review['misuse_id'], $this->decided_review['reviewer_id'], $this->decided_review['review_comment'], $this->decided_review['review_hit']);
        $this->reviewController->updateOrCreateReview($this->undecided_review['misuse_id'], $this->undecided_review['reviewer_id'], $this->undecided_review['review_comment'], $this->decided_review['review_hit']);
        $runs = $this->runController->getRuns($this->detector, $this->experiment, 2);
        self::assertEquals(2, sizeof($runs[0]->misuses));
    }

    function test_one_inconclusive_review()
    {
        $this->reviewController->updateOrCreateReview($this->undecided_review['misuse_id'], $this->undecided_review['reviewer_id'], $this->undecided_review['review_comment'], $this->undecided_review['review_hit']);
        $runs = $this->runController->getRuns($this->detector, $this->experiment, 2);
        self::assertEquals(3, sizeof($runs[0]->misuses));
    }

    function test_one_conclusive_review()
    {
        $this->reviewController->updateOrCreateReview($this->decided_review['misuse_id'], $this->decided_review['reviewer_id'], $this->decided_review['review_comment'], $this->decided_review['review_hit']);
        $this->reviewController->updateOrCreateReview($this->undecided_review['misuse_id'], $this->undecided_review['reviewer_id'], $this->undecided_review['review_comment'], $this->decided_review['review_hit']);
        $this->reviewController->updateOrCreateReview(2, $this->decided_review['reviewer_id'], $this->decided_review['review_comment'], $this->decided_review['review_hit']);
        $runs = $this->runController->getRuns($this->detector, $this->experiment, 2);
        self::assertEquals(2, sizeof($runs[0]->misuses));
    }

}
