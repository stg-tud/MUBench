<?php

/** @var \Slim\Container $container */

use MuBench\ReviewSite\Models\Reviewer;

$request = $container->request;
$serverParams = $request->getServerparams();
$user_name = array_key_exists('PHP_AUTH_USER', $serverParams) ? $serverParams['PHP_AUTH_USER'] : null;
$user = null;
if($user_name){
    $user = Reviewer::firstOrCreate(['name' => $user_name]);
}
$container['user'] = $user;
