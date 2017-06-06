<?php

require_once "DatabaseTestCase.php";

use MuBench\ReviewSite\Controller\FindingsUploader;
use MuBench\ReviewSite\Model\Detector;

class StoreDetectorTest extends DatabaseTestCase
{
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
        $expected_detector = new Detector("-d-", 1);

        self::assertEquals($expected_detector, $actual_detector);
    }

}
