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

class StatsHelper
{
    private $db;
    private $logger;
    private $routesHelper;

    public function __construct(DBConnection $db, Logger $logger, RoutesHelper $routesHelper)
    {
        $this->db = $db;
        $this->logger = $logger;
        $this->routesHelper = $routesHelper;
    }

    public function result_stats(Request $request, Response $response, array $args) {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->routesHelper->default_ex2_review_size);
        $results = array();
        foreach (array("ex1", "ex2", "ex3") as $experiment) {
            $detectors = $this->db->getDetectors($experiment);
            $results[$experiment] = array();
            foreach ($detectors as $detector) {
                $runs = $this->db->getRuns($detector, $experiment, $ex2_review_size);
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

        return $this->routesHelper->render($this, $request, $response, $args, 'result_stats.phtml',
            ['results' => $results, 'ex2_review_size' => $ex2_review_size]);
    }

    public function tag_stats(Request $request, Response $response, array $args) {
        $results = array();
        $tags = $this->db->getAllTags();
        foreach (array("ex1", "ex2", "ex3") as $experiment) {
            $detectors = $this->db->getDetectors($experiment);
            $results[$experiment] = array();
            $total = array();
            foreach($detectors as $detector) {
                foreach($tags as $tag){
                    if(!array_key_exists($tag['name'], $total)){
                        $total[$tag['name']] = array();
                    }
                    $tagged_misuses = $this->db->getTaggedMisuses($experiment, $detector, $tag['id']);
                    $results[$experiment][$detector->name][$tag['name']] = $tagged_misuses;
                    $total[$tag['name']] = array_merge($total[$tag['name']], $tagged_misuses);
                }
            }
            $results[$experiment]["total"] = $total;
        }
        return $this->routesHelper->render($this, $request, $response, $args, 'tag_stats.phtml',
            ['results' => $results, 'tags' => $tags]);
    }

    public function type_stats(Request $request, Response $response, array $args){
        $results = array();
        foreach($this->db->getAllViolationTypes() as $type){
            $results[$type['name']] = $this->db->getMisuseCountForType($type['id']);
        }
        return $this->routesHelper->render($this, $request, $response, $args, 'type_stats.phtml', ['results' => $results]);
    }
}
