<?php

require_once "DatabaseTestCase.php";

use MuBench\ReviewSite\Controller\FindingsUploader;
use MuBench\ReviewSite\Controller\MetadataController;
use MuBench\ReviewSite\Controller\SnippetUploader;
use MuBench\ReviewSite\Model\Misuse;

class StoreFindingsTest extends DatabaseTestCase
{
    private $request_body;

    function setUp()
    {
        parent::setUp();

        $this->request_body = [
            "detector" => "-d-",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => 42.1,
            "number_of_findings" => 23,
            "-custom-stat-" => "-stat-val-",
            "potential_hits" => [
                [
                    "misuse" => "-m-",
                    "rank" => 0,
                    "target_snippets" => [
                        ["first_line_number" => 5, "code" => "-code-"]
                    ],
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]]
        ];
    }

    function test_store_ex1()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

        $data = json_decode(json_encode($this->request_body));
        $uploader->processData("ex1", $data);
        $detector = $this->db->getOrCreateDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex1");

        $expected_run = [
            "exp" => "ex1",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [],
            "-custom-stat-" => "-stat-val-"
        ];

        self::assertEquals([$expected_run], $runs);
    }

    function test_store_ex2()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

        $data = json_decode(json_encode($this->request_body));
        $uploader->processData("ex2", $data);
        $detector = $this->db->getOrCreateDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex2");

        $expected_run = [
            "exp" => "ex2",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [
                new Misuse(
                    ["misuse" => "0", "snippets" => [0 => ["line" => "5", "snippet" => "-code-", "id" => "1"]], "tags" => []],
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
            ],
            "-custom-stat-" => "-stat-val-",
        ];
        self::assertEquals([$expected_run], $runs);
    }

    function test_store_potential_hit_properties() {
        $uploader = new FindingsUploader($this->db, $this->logger);

        $this->request_body["potential_hits"][] = [
            "rank" => 1,
            "target_snippets" => [],
            "new property" => "-val1-"
        ];
        $data = json_decode(json_encode($this->request_body));
        $uploader->processData("ex2", $data);
        $detector = $this->db->getOrCreateDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex2");

        self::assertEquals($runs[0]["misuses"][1]->getPotentialHits()[0]["new property"], "-val1-");
    }

    function test_store_ex3()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

        $data = json_decode(json_encode($this->request_body));
        $uploader->processData("ex3", $data);
        $detector = $this->db->getOrCreateDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex3");

        $expected_run = [
            "exp" => "ex3",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "misuses" => [],
            "-custom-stat-" => "-stat-val-",
        ];

        self::assertEquals([$expected_run], $runs);
    }

    function test_get_misuse_ex1(){
        $metadataController = new MetadataController($this->db, $this->logger);
        // SMELL currently, this test depends on a pattern in the metadata, because otherwise the metadata is not
        // found for ex1. This should not be necessary anymore, once the findings controller is separated.
        $metadataController->updateMetadata('-p-', '-v-', '-m-', '-desc-',
            ['diff-url' => '-diff-', 'description' => '-fix-desc-'],
            ['file' => '-file-location-', 'method' => '-method-location-'], [],
            [['id' => '-p1-', 'snippet' => ['code' => '-code-', 'first_line' => 42]]], []);

        $findingsUploader = new FindingsUploader($this->db, $this->logger);
        $findingsUploader->processData("ex1", json_decode(<<<EOT
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
EOT
        ));

        $detector = $this->db->getDetector("-d-");
        $misuse = $this->db->getMisuse("ex1", $detector, "-p-", "-v-", "-m-");

        $expected_misuse = new Misuse(
            [
                'misuse' => '-m-',
                'project' => '-p-',
                'version' => '-v-',
                'description' => '-desc-',
                'diff_url' => '-diff-',
                'fix_description' => '-fix-desc-',
                'violation_types' => [],
                'file' => '-file-location-',
                'method' => '-method-location-',
                'snippets' => [],
                'patterns' => [
                    ['name' => '-p1-', 'code' => '-code-', 'line' => 42]
                ],
                'tags' => []
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

    function test_delete_snippet()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

        $data = json_decode(json_encode($this->request_body));
        $uploader->processData("ex2", $data);

        $snippet_uploader = new SnippetUploader($this->db, $this->logger);
        $snippet_uploader->deleteSnippet("1");

        $detector = $this->db->getOrCreateDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex2");


        self::assertFalse($runs[0]["misuses"][0]->hasSnippets());
    }

}
