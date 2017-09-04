<?php

namespace MuBench\ReviewSite\Middleware;


use Slim\Http\Request;
use Slim\Http\Response;
use Slim\Middleware\HttpBasicAuthentication;

class AuthMiddleware extends BaseMiddleware
{
    private $basicAuth;

    public function __construct($container)
    {
        parent::__construct($container);
        $this->basicAuth = new HttpBasicAuthentication([
                "secure" => false, // allow non-HTTPs connection
                "realm" => "Protected",
                "users" => $this->users,
        ]);
    }

    public function __invoke(Request $request, Response $response, callable $next)
    {
        return $this->basicAuth->__invoke($request, $response, $next);
    }
}
