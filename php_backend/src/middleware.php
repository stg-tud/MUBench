<?php
require_once 'ConnectionDB.php';
require_once 'DirectoryHelper.php';

use \Slim\Middleware\HttpBasicAuthentication\PdoAuthenticator;


$app->db = new DBConnection();
$app->db->connectDB('localhost', 'mubench', 'root', 'mubench', $app->getContainer()['logger']);
$app->dir = new DirectoryHelper('./logs', $app->getContainer()['logger']);
