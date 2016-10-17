<?php


use \Slim\Middleware\HttpBasicAuthentication\PdoAuthenticator;

$pdo = new \PDO("mysql:host=localhost;dbname=exampleDB", "root", "Admin2015");

$app->add(new \Slim\Middleware\HttpBasicAuthentication([
    "path" => "/",
    "realm" => "Protected",
    "authenticator" => new PdoAuthenticator([
        "pdo" => $pdo
    ])
]));
