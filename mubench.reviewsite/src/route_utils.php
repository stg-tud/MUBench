<?php

use Slim\Http\Request;
use Slim\Http\Response;

# REFACTOR delete this after migration to controllers

function decodeJsonBody(Request $request) {
    $requestBody = $request->getParsedBody();
    $body = json_decode($requestBody, true);
    if ($body) return $body;
    $body = json_decode($request->getBody(), true);
    if ($body) return $body;
    $body = json_decode($_POST["data"], true);
    return $body;
}

function error_response(Response $response, $code, $message) {
    return $response->withStatus($code)->write($message);
}

function download(Response $response, $file_data, $filename)
{
    $stream = fopen('data://text/plain,' . $file_data, 'r');
    $stream = new \Slim\Http\Stream($stream);
    return $response->withHeader('Content-Type', 'application/force-download')
        ->withHeader('Content-Type', 'application/octet-stream')
        ->withHeader('Content-Disposition', 'attachment; filename="' . $filename . '"')
        ->withHeader('Content-Description', 'File Transfer')
        ->withBody($stream);
}
