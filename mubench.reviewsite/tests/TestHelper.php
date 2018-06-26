<?php

namespace MuBench\ReviewSite\Tests;

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use MuBench\ReviewSite\Models\Finding;

class TestHelper
{
    public static function createFindingWith($experiment, $detector, $misuse)
    {
        $finding = new Finding;
        $finding->setDetector($detector);
        Schema::dropIfExists($finding->getTable());
        if(!Schema::hasTable($finding->getTable())){
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
        }

        $finding->experiment_id = $experiment->id;
        $finding->misuse_id = $misuse->id;
        $finding->project_muid = 'mubench';
        $finding->version_muid = '42';
        $finding->misuse_muid = '0';
        $finding->startline = 113;
        $finding->rank = 1;
        $finding->file = 'Test.java';
        $finding->method = "method(A)";
        $finding->save();
    }
}