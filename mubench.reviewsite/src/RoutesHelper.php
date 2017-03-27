<?php

namespace MuBench\ReviewSite;

use Monolog\Logger;
use MuBench\ReviewSite\Model\DetectorResult;
use MuBench\ReviewSite\Model\Experiment;
use MuBench\ReviewSite\Model\ExperimentResult;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\ReviewState;
use Slim\Http\Response;

class RoutesHelper
{

    protected $logger;
    protected $settings;
    protected $site_base_url;
    protected $public_url_prefix;
    protected $private_url_prefix;
    protected $db;
    protected $user;
    protected $path;
    protected $origin_path;

    public function __construct(Logger $logger, $settings, DBConnection $db)
    {
        $this->logger = $logger;
        $this->db = $db;
        $this->settings = $settings;
        $this->site_base_url = $settings['site_base_url'];
        $this->public_url_prefix = $this->site_base_url . "index.php/";
        $this->private_url_prefix = $this->public_url_prefix . "private/";
        $this->user = "";
        $this->path = "";
        $this->origin_path = "";
    }

    public function index_route($args, $r, $response)
    {
        return $this->render($r, $args, $response, 'index.phtml', []);
    }

    public function overview_route($args, $r, $response)
    {
        return $this->render($r, $args, $response, 'overview.phtml', ["misuses" => $this->db->getAllReviews($this->user)]);
    }

    public function todo_route($args, $r, $response)
    {
        return $this->render($r, $args, $response, 'todo.phtml', ["misuses" => $this->db->getTodo($this->user)]);
    }

    public function detect_route($args, $r, Response $response)
    {
        $detector = $this->db->getOrCreateDetector($args['detector']);
        $runs = $this->db->getRuns($detector, $args['exp']);
        return $this->render($r, $args, $response, 'detector.phtml', ['runs' => $runs]);
    }

    public function review_route($args, $r, $response)
    {
        $detector = $this->db->getOrCreateDetector($args['detector']);
        $misuse = $this->db->getMisuse($args['exp'], $detector, $args['project'], $args['version'], $args['misuse']);
        $reviewer = array_key_exists('reviewer', $args) ? $args['reviewer'] : $this->user;
        $review = $misuse->getReview($reviewer);
        $is_reviewer = strcmp($this->user, $reviewer) == 0 || strcmp($reviewer, "resolution") == 0;
        return $this->render($r, $args, $response, 'review.phtml',
            array('is_reviewer' => $is_reviewer, 'misuse' => $misuse, 'review' => $review));
    }

    public function stats_route($handler, $response, $args, $ex2_review_size) {
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

        return $this->render($handler, $args, $response, 'stats.phtml', array(
            'results' => $results,
            'ex2_review_size' => $ex2_review_size
            ));
    }

    private function render($r, $args, $response, $template, $params)
    {
        $params["user"] = $this->user;

        $params["site_base_url"] = htmlspecialchars($this->site_base_url);
        $params["public_url_prefix"] = htmlspecialchars($this->public_url_prefix);
        $params["private_url_prefix"] = htmlspecialchars($this->private_url_prefix);
        $params["url_prefix"] = $params["user"] ? $params["private_url_prefix"] : $params["public_url_prefix"];

        $params["path"] = htmlspecialchars($this->path);
        $params["origin_param"] = htmlspecialchars("?origin=" . $this->path);
        $params["origin_path"] = htmlspecialchars($this->origin_path);

        $params["experiments"] = Experiment::all();
        $params["detectors"] = [];
        foreach ($params["experiments"] as $experiment) { /** @var Experiment $experiment */
            $params["detectors"][$experiment->getId()] = $this->db->getDetectors($experiment->getId());
        }
        $params["experiment"] = array_key_exists("exp", $args) ? Experiment::get($args["exp"]) : null;
        $params["detector"] = array_key_exists("detector", $args) ? $this->db->getOrCreateDetector($args["detector"]) : null;
        return $r->renderer->render($response, $template, $params);
    }

    public function setAuth($user){
        $this->user = $user;
    }

    public function setPath($path){
        if(strcmp($path, "/") === 0) return;
        $this->path = $path;
    }

    public function setOriginPath($origin_path){
        $this->origin_path = $origin_path;
    }
}
