<?php

use Interop\Container\ContainerInterface;
use MuBench\ReviewSite\DBConnection;
use MuBench\ReviewSite\Error;
use Slim\Views\PhpRenderer;

$container = $app->getContainer();

$container['renderer'] = function (ContainerInterface $c) {
    $settings = $c->get('settings')['renderer'];
    return new PhpRenderer($settings['template_path']);
};

$container['logger'] = function (ContainerInterface $c) {
    $settings = $c->get('settings')['logger'];
    $logger = new Monolog\Logger($settings['name']);
    $logger->pushProcessor(new Monolog\Processor\UidProcessor());
    $formatter = new \Monolog\Formatter\LineFormatter();
    $formatter->includeStacktraces();
    $handler = new Monolog\Handler\RotatingFileHandler($settings['path'], 7, $settings['level']);
    $handler->setFormatter($formatter);
    $logger->pushHandler($handler);
    return $logger;
};

$container['errorHandler'] = function (ContainerInterface $c) {
    return new Error($c['logger'], $c->get('settings')['settings']['displayErrorDetails']);
};

$container['database'] = function (ContainerInterface $c) {
    $settings = $c->get('db');
    $logger = $c->get('logger');
    return new DBConnection(new \Pixie\Connection($settings['driver'], $settings), $logger);
};
