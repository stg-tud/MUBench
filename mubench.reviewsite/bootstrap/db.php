<?php

/** @var \Slim\Container $container */

$capsule = new \Illuminate\Database\Capsule\Manager;
$capsule->addConnection($container->settings['db']);
$capsule->setAsGlobal();

use Illuminate\Container\Container;
use Illuminate\Events\Dispatcher;

$capsule->setEventDispatcher(new Dispatcher(new Container()));
$capsule->bootEloquent();

$container['capsule'] = $capsule;

// The schema accesses the database through the app, which we do not have in
// this context. Therefore, use an array to provide the database. This seems
// to work fine.
/** @noinspection PhpParamsInspection */

\Illuminate\Support\Facades\Schema::setFacadeApplication(["db" => $capsule]);
