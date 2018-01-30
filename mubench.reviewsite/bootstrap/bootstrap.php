<?php

use Illuminate\Support\Facades\Schema;

$container = $app->getContainer();

require __DIR__ . '/logger.php';

require __DIR__ . '/db.php';

require __DIR__ . '/auth.php';

require __DIR__ . '/renderer.php';

$exp = new \MuBench\ReviewSite\Models\Experiment;
if(!Schema::hasTable($exp->getTable())){
    header('Location: '.'/../setup/setup.php');
}
