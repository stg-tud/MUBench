<?php

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;


echo 'Creating experiments<br/>';
$experiment1 = new \MuBench\ReviewSite\Models\Experiment;
Schema::dropIfExists($experiment1->getTable());
Schema::create($experiment1->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->string('name', 100);
});
$experiment1->id = 1;
$experiment1->name = "Provided Patterns";
$experiment1->save();
$experiment2 = new \MuBench\ReviewSite\Models\Experiment;
$experiment2->id = 2;
$experiment2->name = "All Findings";
$experiment2->save();
$experiment3 = new \MuBench\ReviewSite\Models\Experiment;
$experiment3->id = 3;
$experiment3->name = "Benchmark";
$experiment3->save();

echo 'Creating detectors table<br/>';
Schema::dropIfExists('detectors');
Schema::create('detectors', function (Blueprint $table) {
    // 'muid' is the primary key here, therefore, we cannot define 'id' as increments, because if we do Eloquent
    // automatically uses it as primary key. To fix this, we manage the id ourselves in the Detector class.
    $table->integer('id');
    $table->string('muid', 100);
    $table->unique(['id']);
    $table->unique(['muid']);
});

echo 'Creating finding snippet<br/>';
$snippet = new \MuBench\ReviewSite\Models\Snippet;
Schema::dropIfExists($snippet->getTable());
Schema::create($snippet->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->string('project_muid', 50);
    $table->string('version_muid', 30);
    $table->string('misuse_muid', 30);
    $table->string('file', 32);
    $table->integer('line');
    $table->text('snippet');
    $table->unique(['project_muid', 'version_muid', 'misuse_muid', 'file', 'line'], 'misuse_snippets');
});

echo 'Creating misuses (metadata)<br/>';
$metadata = new \MuBench\ReviewSite\Models\Metadata;
Schema::dropIfExists($metadata->getTable());
Schema::create($metadata->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->string('project_muid', 50);
    $table->string('version_muid', 30);
    $table->string('misuse_muid', 30);
    $table->text('description');
    $table->text('fix_description');
    $table->text('file');
    $table->text('method');
    $table->text('diff_url');
    $table->dateTime('created_at');
    $table->dateTime('updated_at');

    $table->unique(['project_muid', 'version_muid', 'misuse_muid']);
});

echo 'Creating pattern<br/>';
$pattern = new \MuBench\ReviewSite\Models\Pattern;
Schema::dropIfExists($pattern->getTable());
Schema::create($pattern->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->integer('metadata_id');
    $table->text('code');
    $table->text('line');
});

echo 'Creating misuses<br/>';
$misuse = new \MuBench\ReviewSite\Models\Misuse;
Schema::dropIfExists($misuse->getTable());
Schema::create($misuse->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->integer('detector_id');
    $table->integer('run_id');
    $table->string('misuse_muid', 30);
    $table->integer('metadata_id')->nullable();
    $table->dateTime('created_at');
    $table->dateTime('updated_at');

    $table->unique(['detector_id', 'run_id', 'misuse_muid']);
});

echo 'Creating review<br/>';
$review = new \MuBench\ReviewSite\Models\Review;
Schema::dropIfExists($review->getTable());
Schema::create($review->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->integer('misuse_id');
    $table->integer('reviewer_id');
    $table->text('comment');
    $table->dateTime('created_at');
    $table->dateTime('updated_at');
});

echo 'Creating reviewer<br/>';
$reviewer = new \MuBench\ReviewSite\Models\Reviewer;
Schema::dropIfExists($reviewer->getTable());
Schema::create($reviewer->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->string('name', 50)->unique();
});
$reviewer->name = 'resolution';
$reviewer->save();

echo 'Creating finding reviews<br/>';
$findingReview = new \MuBench\ReviewSite\Models\FindingReview;
Schema::dropIfExists($findingReview->getTable());
Schema::create($findingReview->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->integer('review_id');
    $table->text('decision');
    $table->integer('rank');
});

echo 'Creating Violation Types<br/>';
$type = new \MuBench\ReviewSite\Models\Type;
Schema::dropIfExists($type->getTable());
Schema::create($type->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->text('name');
});

echo 'Creating Violation Types for metadata misuses<br/>';
Schema::dropIfExists('metadata_types');
Schema::create('metadata_types', function (Blueprint $table) {
    $table->increments('id');
    $table->integer('metadata_id');
    $table->integer('type_id');
});

echo 'Creating Violation Types for finding review<br/>';
Schema::dropIfExists('finding_review_types');
Schema::create('finding_review_types', function (Blueprint $table) {
    $table->increments('id');
    $table->integer('finding_review_id');
    $table->integer('type_id');
});

echo 'Creating Tags<br/>';
$tag = new \MuBench\ReviewSite\Models\Tag;
Schema::dropIfExists($tag->getTable());
Schema::create($tag->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->text('name');
    $table->string('color', 7);
});

echo 'Creating MisuseTag<br/>';
Schema::dropIfExists('misuse_tags');
Schema::create('misuse_tags', function (Blueprint $table) {
    $table->increments('id');
    $table->integer('misuse_id');
    $table->integer('tag_id');
    $table->unique(['tag_id', 'misuse_id']);
});
