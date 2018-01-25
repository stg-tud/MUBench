<?php

use MuBench\ReviewSite\LoggingError;

$container['logger'] = function ($c) {
    $settings = $c->settings['logger'];
    $logger = new Monolog\Logger($settings['name']);
    $logger->pushProcessor(new Monolog\Processor\UidProcessor());
    $formatter = new \Monolog\Formatter\LineFormatter();
    $formatter->includeStacktraces();
    $handler = new Monolog\Handler\RotatingFileHandler($settings['path'], 7, $settings['level']);
    $handler->setFormatter($formatter);
    $logger->pushHandler($handler);
    return $logger;
};

$container['errorHandler'] = function ($c) {
    return new LoggingError($c->logger, $c->settings['displayErrorDetails']);
};
