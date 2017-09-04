<?php

session_start();
date_default_timezone_set('Europe/Berlin');

require __DIR__ . '/vendor/autoload.php';

$settings = require __DIR__ . '/src/settings.php';
$app = new \Slim\App($settings);

$container = $app->getContainer();

require __DIR__ . '/bootstrap/bootstrap.php';

require __DIR__ . '/src/routes.php';

$app->run();
