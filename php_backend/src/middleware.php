<?php
require_once 'ConnectionDB.php';
require_once 'DirectoryHelper.php';
require_once 'UploadProcessor.php';
require_once 'DataProcessor.php';
require_once 'RoutesHelper.php';
require_once 'QueryBuilder.php';

$app->add(new \Slim\Middleware\HttpBasicAuthentication([
    "path" => ["/api/", "/private/"],
    "secure" => false,
    "realm" => "Protected",
    "users" => $settings['users']
]));

$servername = $settings['db']['url'];
$dbname = $settings['db']['name'];
$username = $settings['db']['user'];
$password = $settings['db']['password'];

$pdo = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->setAttribute(PDO::MYSQL_ATTR_USE_BUFFERED_QUERY, true);

$logger = $app->getContainer()['logger'];
$db = new DBConnection($pdo, $logger);
$queryBuilder = new QueryBuilder($pdo, $logger);
$app->upload = new UploadProcessor($db, $queryBuilder, $logger);
$app->dir = new DirectoryHelper($settings['upload'], $logger);
$app->data = new DataProcessor($db, $logger);
$app->helper = new RoutesHelper($logger, $settings);