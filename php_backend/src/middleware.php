<?php
require_once 'sql/sql.php';

use \Slim\Middleware\HttpBasicAuthentication\PdoAuthenticator;

$pdo = get_db_connection();


$app->add(new \Slim\Middleware\HttpBasicAuthentication([
    "path" => "/index.php/api",
    "realm" => "Protected",
    "authenticator" => new PdoAuthenticator([
        "pdo" => $pdo
    ])
]));