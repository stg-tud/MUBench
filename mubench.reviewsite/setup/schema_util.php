<?php

use Illuminate\Database\Schema\Blueprint;

require_once __DIR__ . "/Schema.php";


function createTables($connection)
{
    $schema = new Schema($connection);

    echo 'Creating experiments<br/>';
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\Experiment::class, function (Blueprint $table) {
        $table->increments('id');
        $table->string('name', 100);
    });

    echo 'Creating detectors table<br/>';
    $schema->dropIfExistsAndCreateTable('detectors',function (Blueprint $table) {
        // 'muid' is the primary key here, therefore, we cannot define 'id' as increments, because if we do Eloquent
        // automatically uses it as primary key. To fix this, we manage the id ourselves in the Detector class.
        $table->integer('id');
        $table->string('muid', 100);
        $table->unique(['id']);
        $table->unique(['muid']);
    });

    echo 'Creating finding snippet<br/>';
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\Snippet::class, function (Blueprint $table) {
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
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\Metadata::class, function (Blueprint $table) {
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
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\CorrectUsage::class, function (Blueprint $table) {
        $table->increments('id');
        $table->integer('metadata_id');
        $table->text('code');
        $table->text('line');
    });

    echo 'Creating misuses<br/>';
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\Misuse::class, function (Blueprint $table) {
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
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\Review::class, function (Blueprint $table) {
        $table->increments('id');
        $table->integer('misuse_id');
        $table->integer('reviewer_id');
        $table->text('comment');
        $table->dateTime('created_at');
        $table->dateTime('updated_at');
        $table->unique(['misuse_id', 'reviewer_id']);
    });

    echo 'Creating reviewer<br/>';
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\Reviewer::class, function (Blueprint $table) {
        $table->increments('id');
        $table->string('name', 50)->unique();
    });


    echo 'Creating finding reviews<br/>';
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\FindingReview::class, function (Blueprint $table) {
        $table->increments('id');
        $table->integer('review_id');
        $table->text('decision');
        $table->integer('rank');
        $table->unique(['review_id', 'rank']);
    });

    echo 'Creating Violations<br/>';
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\Violation::class, function (Blueprint $table) {
        $table->increments('id');
        $table->text('name');
    });

    echo 'Creating Violations for metadata misuses<br/>';
    $schema->dropIfExistsAndCreateTable('metadata_types', function (Blueprint $table) {
        $table->increments('id');
        $table->integer('metadata_id');
        $table->integer('type_id');
    });

    echo 'Creating Violations for finding review<br/>';
    $schema->dropIfExistsAndCreateTable('finding_review_types', function (Blueprint $table) {
        $table->increments('id');
        $table->integer('finding_review_id');
        $table->integer('type_id');
    });

    echo 'Creating Tags<br/>';
    $schema->dropIfExistsAndCreateTable(\MuBench\ReviewSite\Models\Tag::class, function (Blueprint $table) {
        $table->increments('id');
        $table->text('name');
        $table->string('color', 7);
    });

    echo 'Creating MisuseTag<br/>';
    $schema->dropIfExistsAndCreateTable('misuse_tags', function (Blueprint $table) {
        $table->increments('id');
        $table->integer('misuse_id');
        $table->integer('tag_id');
        $table->unique(['tag_id', 'misuse_id']);
    });

    $experiment1 = new \MuBench\ReviewSite\Models\Experiment;
    $experiment1->id = 1;
    $experiment1->name = "Recall Upper Bound";
    $experiment1->setConnection($connection);
    $experiment1->save();
    $experiment2 = new \MuBench\ReviewSite\Models\Experiment;
    $experiment2->id = 2;
    $experiment2->name = "Precision";
    $experiment2->setConnection($connection);
    $experiment2->save();
    $experiment3 = new \MuBench\ReviewSite\Models\Experiment;
    $experiment3->id = 3;
    $experiment3->name = "Recall";
    $experiment3->setConnection($connection);
    $experiment3->save();

    $reviewer = new \MuBench\ReviewSite\Models\Reviewer;
    $reviewer->setConnection($connection);
    $reviewer->name = 'resolution';
    $reviewer->save();
}
