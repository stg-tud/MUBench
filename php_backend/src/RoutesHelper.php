<?php

use Monolog\Logger;
use MuBench\Detector;

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

    public function review_status($request, $args, $app, $r, $response, $logged)
    {
        $reviews = $app->data->getReviewStatus();
        return $this->render($r, $args, $response, 'status.phtml', array('experiments' => $reviews));
    }

    public function index_route($request, $args, $app, $r, $response, $logged)
    {
        return $this->render($r, $args, $response, 'index.phtml',
            array('experiments' => $this->settings['ex_template'], "logged" => $logged));
    }

    public function experiment_route($request, $args, $app, $r, $response, $logged)
    {
        $exp = $args['exp'];
        $detectors = $app->data->getDetectors2($exp);
        $template = $this->settings['ex_template'][$exp];
        return $this->render($r, $args, $response, 'experiment.phtml',
            array('detectors' => $detectors, 'id' => $template['id'], 'title' => $template['title'], 'exp' => $exp,
                'logged' => $logged));
    }

    public function overview_route($request, $args, $app, $r, $response)
    {
        $reviews = $app->data->getReviewsByReviewer($request->getServerParams()['PHP_AUTH_USER']);
        return $this->render($r, $args, $response, 'overview.phtml',
            array("name" => $request->getServerParams()['PHP_AUTH_USER'], "experiments" => $reviews));
    }

    public function todo_route($request, $args, $app, $r, $response)
    {
        $reviews = $app->data->getTodo($request->getServerParams()['PHP_AUTH_USER']);
        return $this->render($r, $args, $response, 'todo.phtml', array("experiments" => $reviews));
    }

    public function detect_route($request, $args, $app, $r, $response, $logged)
    {
        $exp = $args['exp'];
        $detector = $args['detector'];
        if (!($exp === "ex1" || $exp === "ex2" || $exp === "ex3") || $detector == "") {
            return $response->withStatus(404);
        }
        $name = "";
        if ($logged) {
            $name = $request->getServerParams()['PHP_AUTH_USER'];
        }

        $det = $app->data->getDetector($detector);
        $runs = $app->data->getRuns($det, $exp);

        return $this->render($r, $args, $response, 'detector.phtml',
            array('logged' => $logged, 'name' => $name,
                'exp' => $exp, 'detector' => $detector, 'runs' => $runs));
    }

    public function review_route($args, $app, $r, $response, $request, $logged, $review_flag)
    {
        $exp = $args['exp'];
        $detector = $args['detector'];
        $project = $args['project'];
        $version = $args['version'];
        $misuse = $args['misuse'];

        $det = $app->data->getDetector($detector);
        $misuse = $app->data->getMisuse($exp, $det, $project, $version, $misuse);

        $reviewer = "";
        if ($review_flag && !$logged) {
            $reviewer = $args['reviewer'];
            $logged = $this->isLoggedIn($request, $reviewer);
        } else if ($review_flag && $logged) {
            $reviewer = $request->getServerParams()['PHP_AUTH_USER'];
        }
        return $this->render($r, $args, $response, 'review.phtml',
            array('logged' => $logged, 'name' => $reviewer, 'exp' => $exp, 'detector' => $detector,
                'misuse' => $misuse, 'review' => $misuse->getReview($reviewer)));
    }

    private function isLoggedIn($request, $reviewer)
    {
        if (array_key_exists('PHP_AUTH_USER', $request->getServerParams()) &&
            $request->getServerParams()['PHP_AUTH_USER'] &&
            $request->getServerParams()['PHP_AUTH_USER'] === $reviewer
        ) {
            return true;
        }
        return false;
    }

    private function render($r, $args, $response, $template, $params)
    {
        $params["root_url"] = htmlspecialchars($this->root_url);
        $params["base_url"] = htmlspecialchars($this->base_url);
        $params["private_url"] = htmlspecialchars($this->private_url);
        // TODO add auth information here as well
        $params["experiment"] = array_key_exists("exp", $args) ? $args["exp"] : null;
        $params["detector"] = array_key_exists("detector", $args) ? $args["detector"] : null;
        return $r->renderer->render($response, $template, $params);
    }
}
