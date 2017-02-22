<?php
require_once 'DBConnection.php';
require_once 'DirectoryHelper.php';
require_once 'RoutesHelper.php';

require_once 'MuBench/Detector.php';
require_once 'MuBench/Misuse.php';
require_once 'MuBench/Review.php';
require_once 'MuBench/Results.php';

$app->add(new \Slim\Middleware\HttpBasicAuthentication([
    "path" => ["/api/", "/private/"],
    "secure" => false,
    "realm" => "Protected",
    "users" => $settings['users'],
    "callback" => function ($request, $response, $arguments) use ($app){
        $app->helper->setAuth($request->getServerParams()['PHP_AUTH_USER']);
    }
]));

$servername = $settings['db']['url'];
$dbname = $settings['db']['name'];
$username = $settings['db']['user'];
$password = $settings['db']['password'];

$pdo = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->setAttribute(PDO::MYSQL_ATTR_USE_BUFFERED_QUERY, true);
$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

$logger = $app->getContainer()['logger'];
$db = new DBConnection($pdo, $logger);
$app->db = $db;
$app->dir = new DirectoryHelper($settings['upload'], $logger);
$app->helper = new RoutesHelper($logger, $settings, $db);