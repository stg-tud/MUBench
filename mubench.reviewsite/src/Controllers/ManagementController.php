<?php

namespace MuBench\ReviewSite\Controllers;


use Slim\Http\Request;
use Slim\Http\Response;

class ManagementController extends Controller
{
    public function manage(Request $request, Response $response)
    {
        return $this->renderer->render($response, 'index.phtml');
    }
}