<?php

use Monolog\Logger;
use PHPUnit\Framework\TestCase;
use MuBench\ReviewSite\Model\ExperimentResult;
use MuBench\ReviewSite\Model\DetectorResult;
use MuBench\ReviewSite\Model\Detector;
use MuBench\ReviewSite\Model\Misuse;
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
            new Detector("-d-", 1)
            , [[
            "exp" => "ex1",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0"],
                [0 => []],
                []
            )],
        ]]);
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,\ndetector,project,synthetics,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall\n-d-,1,0,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0\nTotal,1,0,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0';

        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex1", $stats));
    }

    public function test_csv_from_stats_ex2()
    {
        $stats = [];
        $stats[1] = new DetectorResult(
            new Detector("-d-", 1)
            , [[
            "exp" => "ex2",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0"],
                [0 => []],
                []
            )],
        ]]);
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,\ndetector,project,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,precision\n-d-,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0\nTotal,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0';

        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex2", $stats));
    }

    public function test_csv_from_stats_ex3()
    {
        $stats = [];
        $stats[1] = new DetectorResult(
            new Detector("-d-", 1)
            , [[
            "exp" => "ex3",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [new Misuse(
                ["misuse" => "0"],
                [0 => []],
                []
            )],
        ]]);
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,\ndetector,project,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall\n-d-,1,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0\nTotal,1,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0';

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
            "misuses" => [],
            "-custom-stat-" => "-stat-val-",
        ]];
        $expected_csv = 'sep=,\nproject,version,result,number_of_findings,runtime,misuse,decision,resolution_decision,resolution_comment,review1_name,review1_decision,review1_comment\n-p-,-v-,success,23,42.1';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromRuns($runs));
    }

}