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

    public function test_headers_for_stats_ex1()
    {
        $expected_header = "detector,project,synthetics,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        self::assertEquals($expected_header, $this->csv_helper->getCSVHeaderForStatsExp("ex1"));
    }

    public function test_headers_for_stats_ex2()
    {
        $expected_header = "detector,project,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        self::assertEquals($expected_header, $this->csv_helper->getCSVHeaderForStatsExp("ex2"));
    }

    public function test_headers_for_stats_ex3()
    {
        $expected_header = "detector,project,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        self::assertEquals($expected_header, $this->csv_helper->getCSVHeaderForStatsExp("ex3"));
    }

    public function test_csv_from_stats()
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
                ["misuse" => "0", "snippets" => [0 => ["line" => "5", "snippet" => "-code-", "id" => "1"]]],
                [0 => [
                    "exp" => "ex2",
                    "project" => "-p-",
                    "version" => "-v-",
                    "misuse" => "0",
                    "rank" => "0",
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]
                ],
                []
            )],
            "-custom-stat-" => "-stat-val-",
        ]]);
        $stats["total"] = new ExperimentResult($stats);

        $expected_csv = 'sep=,
detector,project,synthetics,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall
-d-,1,0,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0,
Total,1,0,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0,';

        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromStats("ex1", $stats));
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
        $expected_csv = 'sep=,
project,version,result,number_of_findings,runtime,misuse,decision,resolution_decision,resolution_comment,review1_name,review1_decision,review1_comment
-p-,-v-,success,23,42.1,';
        self::assertEquals($expected_csv, $this->csv_helper->createCSVFromRuns($runs));
    }

}