<?php

use Monolog\Logger;
use Slim\Http\Request;
use Slim\Http\Response;

function decodeJsonBody(Request $request) {
    $requestBody = $request->getParsedBody();
    $body = json_decode($requestBody);
    if ($body) return $body;
    $body = json_decode($request->getBody());
    if ($body) return $body;
    $body = json_decode($_POST["data"]);
    return $body;
}

function error_response(Response $response, Logger $logger, $code, $message) {
    $logger->error($message);
    return $response->withStatus($code)->write($message);
}
