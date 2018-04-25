<?php

use Illuminate\Database\Schema\Blueprint;

echo 'Creating experiments<br/>';
$experiment1 = new \MuBench\ReviewSite\Models\Experiment;
$schema->dropIfExists($experiment1->getTable());
$schema->create($experiment1->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->string('name', 100);
});
$experiment1->id = 1;
$experiment1->name = "Recall Upper Bound";
$experiment1->setConnection($schema->getConnection()->getName());
$experiment1->save();
$experiment2 = new \MuBench\ReviewSite\Models\Experiment;
$experiment2->id = 2;
$experiment2->name = "Precision";
$experiment2->setConnection($schema->getConnection()->getName());
$experiment2->save();
$experiment3 = new \MuBench\ReviewSite\Models\Experiment;
$experiment3->id = 3;
$experiment3->name = "Recall";
$experiment3->setConnection($schema->getConnection()->getName());
$experiment3->save();

echo 'Creating detectors table<br/>';
$schema->dropIfExists('detectors');
$schema->create('detectors', function (Blueprint $table) {
    // 'muid' is the primary key here, therefore, we cannot define 'id' as increments, because if we do Eloquent
    // automatically uses it as primary key. To fix this, we manage the id ourselves in the Detector class.
    $table->integer('id');
    $table->string('muid', 100);
    $table->unique(['id']);
    $table->unique(['muid']);
});

echo 'Creating finding snippet<br/>';
$snippet = new \MuBench\ReviewSite\Models\Snippet;
$schema->dropIfExists($snippet->getTable());
$schema->create($snippet->getTable(), function (Blueprint $table) {
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
$schema->dropIfExists($metadata->getTable());
$schema->create($metadata->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->string('project_muid', 50);
    $table->string('version_muid', 30);
    $table->string('misuse_muid', 30);
    $table->text('description');
    $table->text('fix_description');
    $table->text('file');
    $table->text('method');
    $table->text('line');
    $table->text('diff_url');
    $table->dateTime('created_at');
    $table->dateTime('updated_at');

    $table->unique(['project_muid', 'version_muid', 'misuse_muid']);
});

echo 'Creating correct usages<br/>';
$correct_usage = new \MuBench\ReviewSite\Models\CorrectUsage;
$schema->dropIfExists($correct_usage->getTable());
$schema->create($correct_usage->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->integer('metadata_id');
    $table->text('code');
    $table->text('line');
});

echo 'Creating misuses<br/>';
$misuse = new \MuBench\ReviewSite\Models\Misuse;
$schema->dropIfExists($misuse->getTable());
$schema->create($misuse->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->integer('run_id');
    $table->integer('detector_id');
    $table->string('misuse_muid', 30);
    $table->integer('metadata_id')->nullable();
    $table->dateTime('created_at');
    $table->dateTime('updated_at');

    $table->unique(['run_id', 'detector_id', 'misuse_muid']);
});

echo 'Creating review<br/>';
$review = new \MuBench\ReviewSite\Models\Review;
$schema->dropIfExists($review->getTable());
$schema->create($review->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->integer('misuse_id');
    $table->integer('reviewer_id');
    $table->text('comment');
    $table->dateTime('created_at');
    $table->dateTime('updated_at');
    $table->unique(['misuse_id', 'reviewer_id']);
});

echo 'Creating reviewer<br/>';
$reviewer = new \MuBench\ReviewSite\Models\Reviewer;
$schema->dropIfExists($reviewer->getTable());
$schema->create($reviewer->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->string('name', 50)->unique();
});
$reviewer->name = 'resolution';
$reviewer->setConnection($schema->getConnection()->getName());
$reviewer->save();

echo 'Creating finding reviews<br/>';
$findingReview = new \MuBench\ReviewSite\Models\FindingReview;
$schema->dropIfExists($findingReview->getTable());
$schema->create($findingReview->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->integer('review_id');
    $table->text('decision');
    $table->integer('rank');
    $table->unique(['review_id', 'rank']);
});

echo 'Creating Violations<br/>';
$type = new \MuBench\ReviewSite\Models\Violation;
$schema->dropIfExists($type->getTable());
$schema->create($type->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->text('name');
});

echo 'Creating Violations for metadata misuses<br/>';
$schema->dropIfExists('metadata_types');
$schema->create('metadata_types', function (Blueprint $table) {
    $table->increments('id');
    $table->integer('metadata_id');
    $table->integer('type_id');
});

echo 'Creating Violations for finding review<br/>';
$schema->dropIfExists('finding_review_types');
$schema->create('finding_review_types', function (Blueprint $table) {
    $table->increments('id');
    $table->integer('finding_review_id');
    $table->integer('type_id');
});

echo 'Creating Tags<br/>';
$tag = new \MuBench\ReviewSite\Models\Tag;
$schema->dropIfExists($tag->getTable());
$schema->create($tag->getTable(), function (Blueprint $table) {
    $table->increments('id');
    $table->text('name');
    $table->string('color', 7);
});

echo 'Creating MisuseTag<br/>';
$schema->dropIfExists('misuse_tags');
$schema->create('misuse_tags', function (Blueprint $table) {
    $table->increments('id');
    $table->integer('misuse_id');
    $table->integer('tag_id');
    $table->unique(['tag_id', 'misuse_id']);
});
