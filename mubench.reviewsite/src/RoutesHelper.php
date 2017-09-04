<?php

namespace MuBench\ReviewSite;

use Monolog\Logger;
use MuBench\ReviewSite\Model\DetectorResult;
use MuBench\ReviewSite\Model\Experiment;
use MuBench\ReviewSite\Model\ExperimentResult;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\ReviewState;
use MuBench\ReviewSite\StatsHelper;
use Slim\Http\Request;
use Slim\Http\Response;
use Slim\Views\PhpRenderer;

class RoutesHelper
{
    private $db;
    private $renderer;
    private $logger;
    private $site_base_url;
    private $upload_path;
    private $default_ex2_review_size;
    private $statsHelper;

    public function __construct(DBConnection $db, PhpRenderer $renderer, Logger $logger, $upload_path, $site_base_url, $default_ex2_review_size)
    {
        $this->db = $db;
        $this->renderer = $renderer;
        $this->logger = $logger;
        $this->site_base_url = $site_base_url;
        $this->upload_path = $upload_path;
        $this->default_ex2_review_size = $default_ex2_review_size;
        $this->statsHelper = new StatsHelper($db, $logger);
    }

    public function index(Request $request, Response $response, array $args) {
        return $this->render($this, $request, $response, $args, 'index.phtml', []);
    }

    public function detector(Request $request, Response $response, array $args) {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);
        $detector = $this->getDetector($args['detector'], $request, $response);
        $runs = $this->db->getRuns($detector, $args['exp'], $ex2_review_size);
        return $this->render($this, $request, $response, $args, 'detector.phtml', ['ex2_review_size' => $ex2_review_size, 'runs' => $runs]);
    }

    public function overview(Request $request, Response $response, array $args) {
        $reviews = $this->db->getAllReviews($this->getUser($request));
        return $this->render($this, $request, $response, $args, 'overview.phtml', ['misuses' => $reviews]);
    }

    public function todos(Request $request, Response $response, array $args) {
        $todos = $this->db->getTodo($this->getUser($request), $this->default_ex2_review_size);
        return $this->render($this, $request, $response, $args, 'todo.phtml', ['misuses' => $todos]);
    }

    public function result_stats(Request $request, Response $response, array $args) {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);
        $results = $this->statsHelper->getResultStats($ex2_review_size);

        return $this->render($this, $request, $response, $args, 'result_stats.phtml',
            ['results' => $results, 'ex2_review_size' => $ex2_review_size]);
    }

    public function tag_stats(Request $request, Response $response, array $args) {
        $results = $this->statsHelper->getTagStats();
        $tags = $this->db->getAllTags();
        return $this->render($this, $request, $response, $args, 'tag_stats.phtml',
            ['results' => $results, 'tags' => $tags]);
    }

    public function type_stats(Request $request, Response $response, array $args){
        $results = $this->statsHelper->getTypeStats();
        return $this->render($this, $request, $response, $args, 'type_stats.phtml', ['results' => $results]);
    }

    private function render($handler, Request $request, Response $response, array $args, $template, array $params)
    {
        $params["user"] = $this->getUser($request);

        $params["site_base_url"] = htmlspecialchars($this->site_base_url);
        $params["public_url_prefix"] = $params["site_base_url"] . "index.php/";
        $params["private_url_prefix"] = $params["site_base_url"] . "index.php/private/";
        $params["api_url_prefix"] = $params["site_base_url"] . "index.php/api/";
        $params["uploads_url_prefix"] = $params["site_base_url"] . $this->upload_path;
        $params["url_prefix"] = $params["user"] ? $params["private_url_prefix"] : $params["public_url_prefix"];

        $path = $request->getUri()->getPath();
        $params["path"] = htmlspecialchars(strcmp($path, "/") === 0 ? "" : $path);
        $params["origin_param"] = htmlspecialchars("?origin=" . $params["path"]);
        $params["origin_path"] = htmlspecialchars($request->getQueryParam("origin", ""));

        $params["experiments"] = Experiment::all();
        $params["detectors"] = [];
        foreach ($params["experiments"] as $experiment) { /** @var Experiment $experiment */
            $params["detectors"][$experiment->getId()] = $this->db->getDetectors($experiment->getId());
        }
        $params["experiment"] = array_key_exists("exp", $args) ? Experiment::get($args["exp"]) : null;

        $params["detector"] = array_key_exists("detector", $args) ? $this->getDetector($args['detector'], $request, $response) : null;

        return $this->renderer->render($response, $template, $params);
    }

    private function getUser(Request $request)
    {
        $params = $request->getServerParams();
        return array_key_exists('PHP_AUTH_USER', $params) ? $params['PHP_AUTH_USER'] : "";
    }

    private function getDetector($detector_name, $request, $response)
    {
        try{
            return $this->db->getDetector($detector_name);
        }catch (\InvalidArgumentException $e){
            throw new \Slim\Exception\NotFoundException($request, $response);
        }
    }
}
