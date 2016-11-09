<?php
require_once 'ConnectionDB.php';
require_once 'DirectoryHelper.php';

use \Slim\Middleware\HttpBasicAuthentication\PdoAuthenticator;

$servername = $settings['db']['url'];
$dbname = $settings['db']['name'];
$username = $settings['db']['user'];
$password = $settings['db']['password'];

$pdo = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION, PDO::MYSQL_ATTR_USE_BUFFERED_QUERY);

$app->db = new DBConnection($pdo, $app->getContainer()['logger']);
$app->dir = new DirectoryHelper($settings['upload'], $app->getContainer()['logger']);
