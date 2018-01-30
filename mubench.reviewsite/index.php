<?php

session_start();
date_default_timezone_set('Europe/Berlin');

require __DIR__ . '/vendor/autoload.php';

$settings = require __DIR__ . '/settings.php';
$app = new \Slim\App($settings);

$container = $app->getContainer();

require __DIR__ . '/bootstrap/bootstrap.php';

$exp = new \MuBench\ReviewSite\Models\Experiment;
if(!Schema::hasTable($exp->getTable())){
    header('Location: '.'/../setup/setup.php');
}

require __DIR__ . '/src/routes.php';

$app->run();
