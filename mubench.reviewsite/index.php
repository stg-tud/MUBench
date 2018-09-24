<?php

use Illuminate\Support\Facades\Schema;

session_start();
date_default_timezone_set('Europe/Berlin');

require __DIR__ . '/vendor/autoload.php';

$settings = require __DIR__ . '/settings.php';

$app = new \Slim\App($settings);

$container = $app->getContainer();

require __DIR__ . '/bootstrap/logger.php';

require __DIR__ . '/bootstrap/db.php';

$exp = new \MuBench\ReviewSite\Models\Experiment;
if(!Schema::hasTable($exp->getTable())){
    if(file_exists(__DIR__ . '/setup/setup.php')){
        header('Location: ./setup/setup.php');
        exit;
    }else{
        die("Database not set up and setup script not found.");
    }
}

require __DIR__ . '/bootstrap/auth.php';

require __DIR__ . '/bootstrap/renderer.php';

require __DIR__ . '/src/routes.php';

$app->run();
