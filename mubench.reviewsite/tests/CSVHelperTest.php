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
    private $no_reviews_misuse;
    private $positive_reviews_misuse;
    private $resolved_review_misuse;


    function setUp()
    {
        $this->csv_helper = new CSVHelper();
        $this->detector1 = new Detector("-d1-", 1);
        $this->detector2 = new Detector("-d2-", 2);
        $positive_review = new Review([
            'name' => '-reviewer1-',
            'comment' => '-comment-',
            'finding_reviews' => [
                [
                    'decision' => 'Yes',
                ]
            ]
        ]);
        $this->no_reviews_misuse = new Misuse(
            ["misuse" => "0"],
            [0 => []],
            []
        );
        $this->positive_reviews_misuse = new Misuse(
            ["misuse" => "0"],
            [0 => []],
            [
                $positive_review,
                new Review([
                    'name' => '-reviewer2-',
                    'comment' => '-comment-',
                    'finding_reviews' => [
                        [
                            'decision' => 'Yes',
                        ]
                    ]
                ])]
        );
        $this->resolved_review_misuse = new Misuse(
            ["misuse" => "0"],
            [0 => []],
            [
                $positive_review,
                new Review([
                    'name' => '-reviewer2-',
                    'comment' => '-comment-',
                    'finding_reviews' => [
                        [
                            'decision' => 'No',
                        ]
                    ]
                ]),
                new Review([
                    'name' => 'resolution',
                    'comment' => '-comment-',
                    'finding_reviews' => [
                        [
                            'decision' => 'Yes',
                        ]
                    ]
                ])]
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
-d2-,1,0,1,1,0,0,1,0,1,0,0,0,1,0,1,1,1
Total,1,0,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,0.5';

        self::assertEquals($expected_csv, $this->csv_helper->exportStatistics("ex1", $stats));
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
-d2-,1,1,0,0,1,0,1,0,0,0,1,0,1,1,1
Total,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,0.5';

        self::assertEquals($expected_csv, $this->csv_helper->exportStatistics("ex2", $stats));
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
-d2-,1,1,1,0,0,1,0,1,0,0,0,1,0,1,1,1
Total,1,1,2,2,0,1,0,1,0,0,0,0.5,0,0.5,1,0.5';

        self::assertEquals($expected_csv, $this->csv_helper->exportStatistics("ex3", $stats));
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
            "misuses" => [$this->positive_reviews_misuse, $this->resolved_review_misuse, $this->no_reviews_misuse],
        ]];
        $expected_csv = 'sep=,
project,version,result,number_of_findings,runtime,misuse,decision,resolution_decision,resolution_comment,review1_name,review1_decision,review1_comment,review2_name,review2_decision,review2_comment
-p-,-v-,success,23,42.1,0,4,,,-reviewer1-,2,"-comment-",-reviewer2-,2,"-comment-"
-p-,-v-,success,23,42.1,0,6,2,"-comment-",-reviewer1-,2,"-comment-",-reviewer2-,0,"-comment-"
-p-,-v-,success,23,42.1,0,1,,';

        self::assertEquals($expected_csv, $this->csv_helper->exportRunStatistics($runs));
    }

}
