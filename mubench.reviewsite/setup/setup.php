<?php

session_start();
date_default_timezone_set('Europe/Berlin');

require __DIR__ . '/../vendor/autoload.php';

$settings = require __DIR__ . '/../settings.php';
$app = new \Slim\App($settings);

$container = $app->getContainer();

require __DIR__ . '/../bootstrap/db.php';

require __DIR__ . '/../setup/create_database_tables.php';
?>
<link rel="stylesheet" type="text/css" href="../css/style.css"/>
<p style="font-weight: bold">
    Setup finished, <a class="button" href="..">click here</a> to return.
</p>

