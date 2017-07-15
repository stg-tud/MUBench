<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\Model\DetectorResult;
use MuBench\ReviewSite\Model\ExperimentResult;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\ReviewState;
use MuBench\ReviewSite\CSVHelper;
use MuBench\ReviewSite\DBConnection;
use Slim\Http\Request;
use Slim\Http\Response;

class DownloadController
{
    private $db;
    private $logger;
    private $default_ex2_review_size;
    private $csv_helper;

    public function __construct(DBConnection $db, Logger $logger, $default_ex2_review_size)
    {
        $this->db = $db;
        $this->logger = $logger;
        $this->default_ex2_review_size = $default_ex2_review_size;
        $this->csv_helper = new CSVHelper();
    }

    public function download_stats(Request $request, Response $response, array $args)
    {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);
        $experiment = $args['exp'];
        $stats = [];
        $detectors = $this->db->getDetectors($experiment);
        foreach ($detectors as $detector) {
            $runs = $this->db->getRuns($detector, $experiment, $ex2_review_size);
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
            $stats[$detector->id] = new DetectorResult($detector, $runs);
        }
        $stats["total"] = new ExperimentResult($stats);

        return $this->download($response, $this->csv_helper->createCSVFromStats($experiment, $stats), "stats_" . $experiment . ".csv");
    }

    public function download_run_stats(Request $request, Response $response, array $args)
    {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);
        $detector = $this->db->getOrCreateDetector($args['detector']);
        $runs = $this->db->getRuns($detector, $args['exp'], $ex2_review_size);
        return $this->download($response, $this->csv_helper->createCSVFromRuns($runs), $args['detector'] . ".csv");
    }

    private function download(Response $response, $file_data, $filename)
    {
        $stream = fopen('data://text/plain,' . $file_data,'r');
        $stream = new \Slim\Http\Stream($stream);
        return $response->withHeader('Content-Type', 'application/force-download')
            ->withHeader('Content-Type', 'application/octet-stream')
            ->withHeader('Content-Disposition', 'attachment; filename="' . $filename . '"')
            ->withHeader('Content-Description', 'File Transfer')
            ->withBody($stream);
    }

}
