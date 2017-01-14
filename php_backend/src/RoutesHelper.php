<?php

use Monolog\Logger;

class RoutesHelper
{

    protected $logger;

    public function __construct(Logger $logger)
    {
        $this->logger = $logger;
    }

    public function dump($var)
    {
        ob_start();
        var_dump($var);
        return ob_get_clean();
    }

    public function detect_route($args, $app, $r, $response, $logged)
    {
        $exp = $args['exp'];
        $detector = $args['detector'];
        if (!($exp === "ex1" || $exp === "ex2" || $exp === "ex3") || $detector == "") {
            return $response->withStatus(404);
        }
        $stats = $app->data->getIndex($exp, $detector);
        if(!$stats){
            return $response->withStatus(404);
        }
        return $r->renderer->render($response, 'detector.phtml',
            array('logged' => $logged, 'exp' => $exp, 'detector' => $detector,
                'projects' => $stats));
    }

    public function review_route($args, $app, $r, $response, $request, $logged, $review_flag)
    {
        $exp = $args['exp'];
        $detector = $args['detector'];
        $project = $args['project'];
        $version = $args['version'];
        $misuse = $args['misuse'];
        $data = $app->data->getMetadata($misuse);
        $patterns = $app->data->getPatterns($misuse);
        $hits = $app->data->getHits($detector, $project, $version, $misuse, $exp);
        if(!$hits){
            return $response->withStatus(404);
        }
        $reviewer = "";
        $review = NULL;
        if ($review_flag && !$logged) {
            $reviewer = $args['reviewer'];
            if($request->getServerParams()['PHP_AUTH_USER'] && $request->getServerParams()['PHP_AUTH_USER'] === $reviewer){
                $logged = true;
            }
        } else if ($review_flag && $logged) {
            $reviewer = $request->getServerParams()['PHP_AUTH_USER'];
        }
        $method = $hits ? ($exp == "ex2" ? $hits[0]['method'] : $data['method']) : "method not found";
        $code = $hits ? $hits[0]['target_snippets'] : "code not found";
        $line = $hits ? $hits[0]['line'] : 0;
        $file = $hits ? ($exp == "ex2" ? $hits[0]['file'] : $data['file']) : "file not found";
        $review = $app->data->getReview($exp, $detector, $project, $version, $misuse, $reviewer);
        return $r->renderer->render($response, 'review.phtml',
            array('name' => $reviewer, 'review' => $review, 'logged' => $logged, 'exp' => $exp,
                'detector' => $detector, 'version' => $version, 'project' => $project, 'misuse' => $misuse,
                'desc' => $data['description'], 'fix_desc' => $data['fix_description'], 'diff_url' => $data['diff_url'],
                'violation_types' => $data['violation_types'],
                'method' => $method,
                'file' => $file,
                'code' => $code, 'line' => $line, 'pattern_code' => $patterns['code'],
                'pattern_line' => $patterns['line'], 'pattern_name' => $patterns['name'], 'hits' => $hits));
    }

}