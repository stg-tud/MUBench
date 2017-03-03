<?php

require_once "DatabaseTestCase.php";

use MuBench\ReviewSite\Controller\FindingsUploader;
use MuBench\ReviewSite\Controller\MetadataUploader;
use MuBench\ReviewSite\Model\Misuse;

class StoreFindingsTest extends DatabaseTestCase
{

    function test_store_ex1()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

        $data = json_decode($this->finding_json);
        $uploader->processData("ex1", $data, $data->{"potential_hits"});
        $detector = $this->db->getDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex1");

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
        $uploader = new FindingsUploader($this->db, $this->logger);

        $data = json_decode($this->finding_json);
        $uploader->processData("ex2", $data, $data->{"potential_hits"});
        $detector = $this->db->getDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex2");

        $expected_run = [
            "exp" => "ex2",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "detector" => "detector_1",
            "misuses" => [
                new Misuse(
                    ["misuse" => "0", "snippets" => [0 => ["line" => "5", "snippet" => "-code-"]]],
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
                )
            ]
        ];
        self::assertEquals([$expected_run], $runs);
    }

    function test_store_ex3()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

        $data = json_decode($this->finding_json);
        $uploader->processData("ex3", $data, $data->{"potential_hits"});
        $detector = $this->db->getDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex3");

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

    function test_get_misuse_ex1(){
        $finding_uploader = new FindingsUploader($this->db, $this->logger);
        $metadata_uploader = new MetadataUploader($this->db, $this->logger);

        $data = json_decode($this->finding_json);
        $metadata = json_decode($this->metadata_json);
        $finding_uploader->processData("ex1", $data, $data->{"potential_hits"});
        $metadata_uploader->processMetaData($metadata);
        $detector = $this->db->getDetector("-d-");
        $misuse = $this->db->getMisuse("ex1", $detector, "-p-", "-v-", "-m-");

        $expected_misuse = new Misuse(
            [
                'misuse' => '-m-',
                'project' => '-p-',
                'version' => '-v-',
                'description' => '-desc-',
                'fix_description' => '-fix-desc-',
                'violation_types' => 'superfluous/condition/null_check',
                'file' => '-f-',
                'method' => '-method-',
                'diff_url' => '-diff-',
                'snippets' => [['line' => '273', 'snippet' => '-code-']],
                'patterns' => [['name' => '-p-id-','code' => '-pattern-code-','line' => '1']]
            ],
            [[
                'exp' => 'ex1',
                'project' => '-p-',
                'version' => '-v-',
                'misuse' => '-m-',
                'rank' => '0',
                'custom1' => '-val1-',
                'custom2' => '-val2-',
            ]],
            []);

        self::assertEquals($expected_misuse, $misuse);
    }

}
