<?php

use Illuminate\Support\Facades\Schema;

$container = $app->getContainer();

require __DIR__ . '/logger.php';

require __DIR__ . '/db.php';

$exp = new \MuBench\ReviewSite\Models\Experiment;
if(!Schema::hasTable($exp->getTable())){
    if(file_exists(__DIR__ . '/../setup/setup.php')){
        header('Location: '.'/../setup/setup.php');
    }else{
        die("Database not set up and setup script not found.");
    }
}

require __DIR__ . '/auth.php';

require __DIR__ . '/renderer.php';
