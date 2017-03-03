<?php

use MuBench\ReviewSite\Error;
use Slim\Views\PhpRenderer;

$container = $app->getContainer();

// view renderer
$container['renderer'] = function ($c) {
    $settings = $c->get('settings')['renderer'];
    return new PhpRenderer($settings['template_path']);
};

// monolog
$container['logger'] = function ($c) {
    $settings = $c->get('settings')['logger'];
    $logger = new Monolog\Logger($settings['name']);
    $logger->pushProcessor(new Monolog\Processor\UidProcessor());
    $logger->pushHandler(new Monolog\Handler\RotatingFileHandler($settings['path'], 7, $settings['level']));
    return $logger;
};

$container['errorHandler'] = function ($c) {
    return new Error($c['logger'], $c->get('settings')['settings']['displayErrorDetails']);
};
