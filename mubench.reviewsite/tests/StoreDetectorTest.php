<?php

require_once "DatabaseTestCase.php";

use MuBench\ReviewSite\Controller\FindingsUploader;
use MuBench\ReviewSite\Model\Detector;

class StoreDetectorTest extends DatabaseTestCase
{

    private $expected_detector;

    function setUp()
    {
        parent::setUp();
        $this->expected_detector = new Detector("-d-", 1);
    }

    function test_create_detector()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

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

        $uploader->processData("ex1", $data);
        $actual_detector = $this->db->getOrCreateDetector("-d-");

        self::assertEquals($this->expected_detector, $actual_detector);
    }

    function test_empty_stats_table_before_upload()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

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

        $this->db->create_table($this->expected_detector->getStatsTableName(), ['`exp` VARCHAR(10) NOT NULL', '`project` VARCHAR(100) NOT NULL', '`version` VARCHAR(100) NOT NULL',
            'PRIMARY KEY(`exp`, `project`, `version`)']);
        $uploader->processData("ex1", $data);
        $actual_detector = $this->db->getOrCreateDetector("-d-");

        self::assertEquals($this->expected_detector, $actual_detector);
    }

}
