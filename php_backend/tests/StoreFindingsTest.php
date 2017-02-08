<?php

require_once "src/QueryBuilder.php";
require_once "src/UploadProcessor.php";
require_once "src/DataProcessor.php";
require_once "src/MuBench/Detector.php";
require_once "src/MuBench/Misuse.php";
require_once "DatabaseTestCase.php";

use MuBench\Detector;
use MuBench\Misuse;

class StoreFindingsTest extends DatabaseTestCase
{
    protected $finding_json = <<<EOT
    {
        "detector": "-d-",
        "project": "-p-",
        "version": "-v-",
        "result": "success",
        "runtime": 42.1,
        "number_of_findings": 23,
        "potential_hits": [
            {
                "misuse": "-m-",
                "rank": 0,
                "target_snippets": [
                    {"first_line_number": 5, "code": "-code-"}
                ],
                "custom1": "-val1-",
                "custom2": "-val2-"
            }
        ]
    }
EOT;

    function test_store_ex1()
    {
        $queryBuilder = new QueryBuilder($this->pdo, $this->logger);
        $upload_processor = new UploadProcessor($this->db, $queryBuilder, $this->logger);
        $data_processor = new DataProcessor($this->db, $this->logger);

        $data = json_decode($this->finding_json);
        $upload_processor->processData("ex1", $data, $data->{"potential_hits"});
        $detector = $data_processor->getDetector("-d-");
        $runs = $data_processor->getRuns($detector, "ex1");

        $expected_run = [
            "exp" => "ex1",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "detector" => "detector_1",
            "misuses" => []
        ];

        self::assertEquals([$expected_run], $runs);
    }

    function test_store_ex2()
    {
        $queryBuilder = new QueryBuilder($this->pdo, $this->logger);
        $upload_processor = new UploadProcessor($this->db, $queryBuilder, $this->logger);
        $data_processor = new DataProcessor($this->db, $this->logger);

        // $this->markTestSkipped('must be revisited.');

        $data = json_decode($this->finding_json);
        $upload_processor->processData("ex2", $data, $data->{"potential_hits"});
        $detector = $data_processor->getDetector("-d-");
        $runs = $data_processor->getRuns($detector, "ex2");

        $expected_run = [
            "exp" => "ex2",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "detector" => "detector_1",
            "misuses" => [ new Misuse(["misuse" => "0"], [0 => [
                "exp" => "ex2",
                "project" => "-p-",
                "version" => "-v-",
                "misuse" => "0",
                "rank" => "0",
                "custom1" => "-val1-",
                "custom2" => "-val2-"
            ]], []) ]
        ];
        self::assertEquals([$expected_run], $runs);
    }

    function test_store_ex3()
    {
        $queryBuilder = new QueryBuilder($this->pdo, $this->logger);
        $upload_processor = new UploadProcessor($this->db, $queryBuilder, $this->logger);
        $data_processor = new DataProcessor($this->db, $this->logger);

        $data = json_decode($this->finding_json);
        $upload_processor->processData("ex3", $data, $data->{"potential_hits"});
        $detector = $data_processor->getDetector("-d-");
        $runs = $data_processor->getRuns($detector, "ex3");

        $expected_run = [
            "exp" => "ex3",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "detector" => "detector_1",
            "misuses" => []
        ];

        self::assertEquals([$expected_run], $runs);
    }

    function test_create_detector()
    {
        $queryBuilder = new QueryBuilder($this->pdo, $this->logger);
        $upload_processor = new UploadProcessor($this->db, $queryBuilder, $this->logger);
        $data_processor = new DataProcessor($this->db, $this->logger);

        $data = json_decode(
            <<<EOD
    {
        "detector": "-d-",
        "project": "-p-",
        "version": "-v-",
        "misuse": "-m-",
        "result": "failure",
        "runtime": 30.1,
        "number_of_findings": 0,
        "potential_hits": []
    }
EOD
        );

        $upload_processor->processData("ex1", $data, $data->{'potential_hits'});
        $actual_detector = $data_processor->getDetector("-d-");
        $expected_detector = new Detector("-d-", 1);

        self::assertEquals($expected_detector, $actual_detector);
    }

    function test_store_metadata()
    {
        $queryBuilder = new QueryBuilder($this->pdo, $this->logger);
        $upload_processor = new UploadProcessor($this->db, $queryBuilder, $this->logger);
        $data_processor = new DataProcessor($this->db, $this->logger);
        $data = json_decode(
            <<<EOD
        {
            "project": "-p-",
            "version": "-v-",
            "misuse": "-m-", 
            "patterns": [
                    {
                        "snippet": {
                            "first_line": 1, 
                            "code": "-pattern-code-"
                        }, 
                        "id": "-p-id-"
                    }
            ], 
            "violation_types": [
                "superfluous/condition/null_check"
            ], 
            "target_snippets": [
                {
                    "first_line_number": 273, 
                    "code": "-code-"
                }
            ], 
            "description": "-desc-", 
            "location": {
                "file": "-f-", 
                "method": "-method-"
            }, 
            "fix": 
                {
                    "diff-url": "-diff-", 
                    "description": "-fix-desc-"
                }
        }
EOD
        );
        $upload_processor->processMetaData($data);
        $actual_metadata = $data_processor->getMetadata("-p-", "-v-", "-m-");
        $actual_snippet = $data_processor->getMetaSnippets("-p-", "-v-", "-m-");

        $expected_metadata = [
            "project" => "-p-",
            "version" => "-v-",
            "misuse" => "-m-",
            "description" => "-desc-",
            "method" => "-method-",
            "diff_url" => "-diff-",
            "fix_description" => "-fix-desc-",
            "file" => "-f-",
            "violation_types" => ["superfluous/condition/null_check"]
        ];
        $expected_snippet = [
            ["snippet" => "-code-", "line" => 273]
        ];

        self::assertEquals($expected_metadata, $actual_metadata);
        self::assertEquals($expected_snippet, $actual_snippet);
    }

}
