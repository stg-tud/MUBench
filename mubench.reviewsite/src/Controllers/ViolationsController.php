<?php

namespace MuBench\ReviewSite\Controllers;


use MuBench\ReviewSite\Models\Violation;
use Slim\Http\Request;
use Slim\Http\Response;

class ViolationsController extends Controller
{

    public function getViolations(Request $request, Response $response, array $args){
        $results = array();
        foreach(Violation::all() as $violation){
            $results[$violation->name] = count($violation->metadata);
        }
        return $this->renderer->render($response, 'violation_stats.phtml', ['results' => $results]);
    }

}
