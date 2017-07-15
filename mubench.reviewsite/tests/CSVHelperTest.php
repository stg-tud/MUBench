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

    function setUp()
    {
        $this->csv_helper = new CSVHelper();
    }

    public function test_csv_from_stats_ex1()
    {
        $stats = [];
        $stats[1] = new DetectorResult(
            new Detector("-d1-", 1)
            , [[
            "exp" => "ex1",
            "project" => "-p1-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0", "snippets" => [0 => ["line" => "5", "snippet" => "-code-", "id" => "1"]]],
                [0 => [
                    "exp" => "ex2",
                    "project" => "-p1-",
                    "version" => "-v-",
                    "misuse" => "0",
                    "rank" => "0",
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]
                ],
                []
            )],
        ]]);
        $stats[2] = new DetectorResult(
            new Detector("-d2-", 1)
            , [[
            "exp" => "ex1",
            "project" => "-p1-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0"],
                [0 => []],
                [new Review([
                    'name' => '-reviewer1-',
                    'exp' => 'ex1',
                    'detector' => 1,
                    'project' => '-p1-',
                    'version' => '-v-',
                    'misuse' => '-m-',
                    'comment' => '-comment-',
                    'id' => '0',
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
                ]),
                    new Review([
                        'name' => '-reviewer2-',
                        'exp' => 'ex1',
                        'detector' => 1,
                        'project' => '-p1-',
                        'version' => '-v-',
                        'misuse' => '-m-',
                        'comment' => '-comment-',
                        'id' => '0',
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
                    ])]
            )],
        ]]);
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,
detector,project,synthetics,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall
-d1-,1,0,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0
-d2-,1,0,1,1,0,0,1,0,1,0,0,0,1,0,1,1,100
Total,1,0,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,50';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex1", $stats));
    }

    public function test_csv_from_stats_ex2()
    {
        $stats = [];
        $stats[1] = new DetectorResult(
            new Detector("-d1-", 1)
            , [[
            "exp" => "ex2",
            "project" => "-p1-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0", "snippets" => [0 => ["line" => "5", "snippet" => "-code-", "id" => "1"]]],
                [0 => [
                    "exp" => "ex2",
                    "project" => "-p1-",
                    "version" => "-v-",
                    "misuse" => "0",
                    "rank" => "0",
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]
                ],
                []
            )],
        ]]);
        $stats[2] = new DetectorResult(
            new Detector("-d2-", 1)
            , [[
            "exp" => "ex2",
            "project" => "-p1-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0"],
                [0 => []],
                [new Review([
                    'name' => '-reviewer1-',
                    'exp' => 'ex2',
                    'detector' => 1,
                    'project' => '-p1-',
                    'version' => '-v-',
                    'misuse' => '-m-',
                    'comment' => '-comment-',
                    'id' => '0',
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
                ]),
                    new Review([
                        'name' => '-reviewer2-',
                        'exp' => 'ex2',
                        'detector' => 1,
                        'project' => '-p1-',
                        'version' => '-v-',
                        'misuse' => '-m-',
                        'comment' => '-comment-',
                        'id' => '0',
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
                    ])]
            )],
        ]]);
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,
detector,project,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,precision
-d1-,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0
-d2-,1,1,0,0,1,0,1,0,0,0,1,0,1,1,100
Total,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,50';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex2", $stats));
    }

    public function test_csv_from_stats_ex3()
    {
        $stats = [];
        $stats[1] = new DetectorResult(
            new Detector("-d1-", 1)
            , [[
            "exp" => "ex3",
            "project" => "-p1-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0", "snippets" => [0 => ["line" => "5", "snippet" => "-code-", "id" => "1"]]],
                [0 => [
                    "exp" => "ex2",
                    "project" => "-p1-",
                    "version" => "-v-",
                    "misuse" => "0",
                    "rank" => "0",
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]
                ],
                []
            )],
        ]]);
        $stats[2] = new DetectorResult(
            new Detector("-d2-", 1)
            , [[
            "exp" => "ex3",
            "project" => "-p1-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0"],
                [0 => []],
                [new Review([
                    'name' => '-reviewer1-',
                    'exp' => 'ex3',
                    'detector' => 1,
                    'project' => '-p1-',
                    'version' => '-v-',
                    'misuse' => '-m-',
                    'comment' => '-comment-',
                    'id' => '0',
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
                ]),
                    new Review([
                        'name' => '-reviewer2-',
                        'exp' => 'ex3',
                        'detector' => 1,
                        'project' => '-p1-',
                        'version' => '-v-',
                        'misuse' => '-m-',
                        'comment' => '-comment-',
                        'id' => '0',
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
                    ])]
            )],
        ]]);
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,
detector,project,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall
-d1-,1,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0
-d2-,1,1,1,0,0,1,0,1,0,0,0,1,0,1,1,100
Total,1,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,50';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex3", $stats));
    }


    function test_csv_from_detector()
    {
        $runs = [[
            "exp" => "ex1",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0"],
                [0 => []],
                [new Review([
                    'name' => '-reviewer1-',
                    'exp' => 'ex3',
                    'detector' => 1,
                    'project' => '-p1-',
                    'version' => '-v-',
                    'misuse' => '-m-',
                    'comment' => '-comment-',
                    'id' => '0',
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
                ]),
                    new Review([
                        'name' => '-reviewer2-',
                        'exp' => 'ex3',
                        'detector' => 1,
                        'project' => '-p1-',
                        'version' => '-v-',
                        'misuse' => '-m-',
                        'comment' => '-comment-',
                        'id' => '0',
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
                    ])]
            )],
            "-custom-stat-" => "-stat-val-",
        ]];
        $expected_csv = 'sep=,
project,version,result,number_of_findings,runtime,misuse,decision,resolution_decision,resolution_comment,review1_name,review1_decision,review1_comment
-p-,-v-,success,23,42.1,0,4,,,-reviewer1-,2,-comment-,-reviewer2-,2,-comment-';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromRuns($runs));
    }

}