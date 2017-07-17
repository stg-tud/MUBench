<?php

use Monolog\Logger;
use PHPUnit\Framework\TestCase;
use MuBench\ReviewSite\Model\ExperimentResult;
use MuBench\ReviewSite\Model\DetectorResult;
use MuBench\ReviewSite\Model\Detector;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\Review;

use \MuBench\ReviewSite\CSVHelper;

class CSVHelperTest extends TestCase
{

    private $csv_helper;
    private $detector1;
    private $detector2;
    private $review1;
    private $review2;
    private $no_reviews_misuse;
    private $positive_reviews_misuse;


    function setUp()
    {
        $this->csv_helper = new CSVHelper();
        $this->detector1 = new Detector("-d1-", 1);
        $this->detector2 = new Detector("-d2-", 2);
        $this->review1 = new Review([
            'name' => '-reviewer1-',
            'comment' => '-comment-',
            'finding_reviews' => [
                [
                    'decision' => 'Yes',
                    'id' => '0',
                    'rank' => '0',
                    'review' => '1',
                    'violation_types' => [
                        'missing/call'
                    ]
                ]
            ]
        ]);
        $this->review2 = new Review([
            'name' => '-reviewer2-',
            'comment' => '-comment-',
            'finding_reviews' => [
                [
                    'decision' => 'Yes',
                    'id' => '0',
                    'rank' => '0',
                    'review' => '1',
                    'violation_types' => [
                        'missing/call'
                    ]
                ]
            ]
        ]);
        $this->no_reviews_misuse = new Misuse(
            ["misuse" => "0"],
            [0 => []
            ],
            []
        );
        $this->positive_reviews_misuse = new Misuse(
            ["misuse" => "0"],
            [0 => []],
            [$this->review1, $this->review2]
        );
    }

    public function test_ex1_stats_as_csv()
    {
        $stats = [
            new DetectorResult(
                $this->detector1
                , [[
                "exp" => "ex1",
                "project" => "-p1-",
                "version" => "-v-",
                "result" => "success",
                "runtime" => "42.1",
                "number_of_findings" => "23",
                "misuses" => [$this->no_reviews_misuse],
            ]]),
            new DetectorResult(
                $this->detector2
                , [[
                "exp" => "ex1",
                "project" => "-p1-",
                "version" => "-v-",
                "result" => "success",
                "runtime" => "42.1",
                "number_of_findings" => "23",
                "misuses" => [$this->positive_reviews_misuse],
            ]])];
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,
detector,project,synthetics,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall
-d1-,1,0,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0
-d2-,1,0,1,1,0,0,1,0,1,0,0,0,1,0,1,1,100
Total,1,0,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,50';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex1", $stats));
    }

    public function test_ex2_stats_as_csv()
    {
        $stats = [
            new DetectorResult(
                $this->detector1
                , [[
                "exp" => "ex2",
                "project" => "-p1-",
                "version" => "-v-",
                "result" => "success",
                "runtime" => "42.1",
                "number_of_findings" => "23",
                "misuses" => [$this->no_reviews_misuse],
            ]]),
            new DetectorResult(
                $this->detector2
                , [[
                "exp" => "ex2",
                "project" => "-p1-",
                "version" => "-v-",
                "result" => "success",
                "runtime" => "42.1",
                "number_of_findings" => "23",
                "misuses" => [$this->positive_reviews_misuse],
            ]])];
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,
detector,project,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,precision
-d1-,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0
-d2-,1,1,0,0,1,0,1,0,0,0,1,0,1,1,100
Total,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,50';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex2", $stats));
    }

    public function test_ex3_stats_as_csv()
    {
        $stats = [
            new DetectorResult(
                $this->detector1
                , [[
                "exp" => "ex3",
                "project" => "-p1-",
                "version" => "-v-",
                "result" => "success",
                "runtime" => "42.1",
                "number_of_findings" => "23",
                "misuses" => [$this->no_reviews_misuse],
            ]]),
            new DetectorResult(
                $this->detector2
                , [[
                "exp" => "ex3",
                "project" => "-p1-",
                "version" => "-v-",
                "result" => "success",
                "runtime" => "42.1",
                "number_of_findings" => "23",
                "misuses" => [$this->positive_reviews_misuse],
            ]])];
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,
detector,project,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall
-d1-,1,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0
-d2-,1,1,1,0,0,1,0,1,0,0,0,1,0,1,1,100
Total,1,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,50';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex3", $stats));
    }


    function test_export_detector_run_as_csv()
    {
        $runs = [[
            "exp" => "ex1",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [$this->positive_reviews_misuse, $this->no_reviews_misuse],
        ]];
        $expected_csv = 'sep=,
project,version,result,number_of_findings,runtime,misuse,decision,resolution_decision,resolution_comment,review1_name,review1_decision,review1_comment
-p-,-v-,success,23,42.1,0,4,,,-reviewer1-,2,-comment-,-reviewer2-,2,-comment-
-p-,-v-,success,23,42.1,0,1,,';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromRuns($runs));
    }

}