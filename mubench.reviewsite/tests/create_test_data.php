<?php

session_start();
date_default_timezone_set('Europe/Berlin');

require __DIR__ . '/../vendor/autoload.php';

$settings = require __DIR__ . '/../settings.php';
$app = new \Slim\App($settings);

$container = $app->getContainer();

require __DIR__ . '/../bootstrap/logger.php';

require __DIR__ . '/../bootstrap/db.php';

require __DIR__ . '/../setup/database_setup_utils.php';

createTables('default');

require __DIR__ . '/create_simple_test_data.php';
