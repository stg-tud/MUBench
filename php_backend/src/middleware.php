<?php
require_once 'ConnectionDB.php';
require_once 'DirectoryHelper.php';

use \Slim\Middleware\HttpBasicAuthentication\PdoAuthenticator;


$app->db = new DBConnection();
$app->db->connectDB($settings['db']['url'], $settings['db']['name'], $settings['db']['user'], $settings['db']['password'], $app->getContainer()['logger']);
$app->dir = new DirectoryHelper('./upload', $app->getContainer()['logger']);
