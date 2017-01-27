<?php

use Monolog\Logger;

class RoutesHelper
{

    protected $logger;
    protected $settings;
    protected $root_url;
    protected $base_url;
    protected $private_url;

    public function __construct(Logger $logger, $settings)
    {
        $this->logger = $logger;
        $this->settings = $settings;
        $this->root_url = $settings['root_url'];
        $this->base_url = $settings['root_url'] . "index.php/";
        $this->private_url = $this->base_url . "private/";
    }

    public function dump($var)
    {
        ob_start();
        var_dump($var);
        return ob_get_clean();
    }

    public function index_route($request, $args, $app, $r, $response, $logged){
        return $r->renderer->render($response, 'index.phtml', array('experiments' => $this->settings['ex_template'], "logged" => $logged, 'base_url' => $this->base_url, 'private_url' => $this->private_url, 'root_url' => $this->root_url));
    }

    public function experiment_route($request, $args, $app, $r, $response, $logged){
        $exp = $args['exp'];
        $data = $app->data->getDetectors($exp);
        $template = $this->settings['ex_template'][$exp];
        return $r->renderer->render($response, 'experiment.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'exp' => $exp, 'logged' => $logged, 'root_url' => $this->root_url, 'private_url' => $this->private_url, 'base_url' => $this->base_url));
    }

    public function overview_route($request, $args, $app, $r, $response){
        $reviews = $app->data->getReviewsByReviewer($request->getServerParams()['PHP_AUTH_USER']);
        return $r->renderer->render($response, 'overview.phtml', array("name" => $request->getServerParams()['PHP_AUTH_USER'], "private_url" => $this->private_url, "experiments" => $reviews));
    }

    public function todo_route($request, $args, $app, $r, $response){
        $reviews = $app->data->getTodo($request->getServerParams()['PHP_AUTH_USER']);
        return $r->renderer->render($response, 'todo.phtml', array("private_url" => $this->private_url, "experiments" => $reviews));
    }

    public function detect_route($request, $args, $app, $r, $response, $logged)
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
        $name = "";
        if($logged){
            $name = $request->getServerParams()['PHP_AUTH_USER'];
        }
        return $r->renderer->render($response, 'detector.phtml',
            array('logged' => $logged, 'name' => $name,
                'exp' => $exp, 'detector' => $detector, 'projects' => $stats, 'base_url' => $this->base_url, 'private_url' => $this->private_url));
    }

    public function review_route($args, $app, $r, $response, $request, $logged, $review_flag)
    {
        $exp = $args['exp'];
        $detector = $args['detector'];
        $project = $args['project'];
        $version = $args['version'];
        $misuse = $args['misuse'];
        $data = $app->data->getMetadata($project, $version, $misuse);
        $patterns = $app->data->getPatterns($misuse);
        $hits = $app->data->getHits($detector, $project, $version, $misuse, $exp);
        $reviewer = "";
        $review = NULL;
        if ($review_flag && !$logged) {
            $reviewer = $args['reviewer'];
            if(array_key_exists('PHP_AUTH_USER', $request->getServerParams()) && $request->getServerParams()['PHP_AUTH_USER'] && $request->getServerParams()['PHP_AUTH_USER'] === $reviewer){
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
                'code' => $code, 'line' => $line, 'patterns' => $patterns, 'hits' => $hits, 'root_url' => $this->root_url, 'base_url' => $this->base_url, 'private_url' => $this->private_url));
    }

}