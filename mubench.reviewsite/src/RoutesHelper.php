<?php

namespace MuBench\ReviewSite;

use Monolog\Logger;
use MuBench\ReviewSite\Model\DetectorResult;
use MuBench\ReviewSite\Model\Experiment;
use MuBench\ReviewSite\Model\ExperimentResult;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\ReviewState;
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

    public function __construct(DBConnection $db, PhpRenderer $renderer, Logger $logger, $upload_path, $site_base_url)
    {
        $this->db = $db;
        $this->renderer = $renderer;
        $this->logger = $logger;
        $this->site_base_url = $site_base_url;
        $this->upload_path = $upload_path;
    }

    public function index(Request $request, Response $response, array $args) {
        return $this->render($this, $request, $response, $args, 'index.phtml', []);
    }

    public function detector(Request $request, Response $response, array $args) {
        $detector = $this->db->getOrCreateDetector($args['detector']);
        $runs = $this->db->getRuns($detector, $args['exp']);
        return $this->render($this, $request, $response, $args, 'detector.phtml', ['runs' => $runs]);
    }

    public function review(Request $request, Response $response, array $args)
    {
        $detector = $this->db->getOrCreateDetector($args['detector']);
        $misuse = $this->db->getMisuse($args['exp'], $detector, $args['project'], $args['version'], $args['misuse']);
        $user = $this->getUser($request);
        $reviewer = array_key_exists('reviewer', $args) ? $args['reviewer'] : $user;
        $review = $misuse->getReview($reviewer);
        $is_reviewer = strcmp($user, $reviewer) == 0 || strcmp($reviewer, "resolution") == 0;
        return $this->render($this, $request, $response, $args, 'review.phtml',
            ['is_reviewer' => $is_reviewer, 'misuse' => $misuse, 'review' => $review]);
    }

    public function stats(Request $request, Response $response, array $args) {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", 20);
        $results = array();
        foreach (array("ex1", "ex2", "ex3") as $experiment) {
            $detectors = $this->db->getDetectors($experiment);
            $results[$experiment] = array();
            foreach ($detectors as $detector) {
                $runs = $this->db->getRuns($detector, $experiment);
                // TODO move this functionality to dedicate experiment classes
                if (strcmp($experiment, "ex2") === 0) {
                    foreach ($runs as &$run) {
                        $misuses = array();
                        $number_of_misuses = 0;
                        foreach ($run["misuses"] as $misuse) { /** @var $misuse Misuse */
                            if ($misuse->getReviewState() != ReviewState::UNRESOLVED) {
                                $misuses[] = $misuse;
                                $number_of_misuses++;
                            }

                            if ($number_of_misuses == $ex2_review_size) {
                                break;
                            }
                        }
                        $run["misuses"] = $misuses;
                    }
                }
                $results[$experiment][$detector->id] = new DetectorResult($detector, $runs);
            }
            $results[$experiment]["total"] = new ExperimentResult($results[$experiment]);
        }

        return $this->render($this, $request, $response, $args, 'stats.phtml',
            ['results' => $results, 'ex2_review_size' => $ex2_review_size]);
    }

    public function overview(Request $request, Response $response, array $args) {
        $reviews = $this->db->getAllReviews($this->getUser($request));
        return $this->render($this, $request, $response, $args, 'overview.phtml', ["misuses" => $reviews]);
    }

    public function todos(Request $request, Response $response, array $args) {
        $todos = $this->db->getTodo($this->getUser($request));
        return $this->render($this, $request, $response, $args, 'todo.phtml', ["misuses" => $todos]);
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
        $params["detector"] = array_key_exists("detector", $args) ? $this->db->getOrCreateDetector($args["detector"]) : null;
        return $this->renderer->render($response, $template, $params);
    }

    private function getUser(Request $request)
    {
        $params = $request->getServerParams();
        return array_key_exists('PHP_AUTH_USER', $params) ? $params['PHP_AUTH_USER'] : "";
    }
}
