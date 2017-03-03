<?php

use MuBench\ReviewSite\DBConnection;
use MuBench\ReviewSite\DirectoryHelper;
use MuBench\ReviewSite\RoutesHelper;
use Slim\Http\Request;
use Slim\Http\Response;

$app->add(new \Slim\Middleware\HttpBasicAuthentication([
    "path" => ["/api/", "/private/"],
    "secure" => false,
    "realm" => "Protected",
    "users" => $settings['users'],
    "callback" => function (Request $request, Response $response, $arguments) use ($app){
        $app->helper->setAuth($request->getServerParams()['PHP_AUTH_USER']);
    }
]));

$app->add(function (Request $request, Response $response, $next) use ($app) {
    $route = $request->getUri()->getPath();
    $origin = $request->getQueryParams();

    if($origin && !empty($origin && array_key_exists('origin', $origin) && strcmp($origin['origin'], "") !== 0)){
        $app->helper->setOrigin($origin['origin']);
    }

    if($route && strcmp($route, "") !== 0 && !empty($route)){
        $app->helper->setRoute($route);
    }

    $response = $next($request, $response);
    return $response;
});

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