<?php

require_once "src/QueryBuilder.php";
require_once "src/UploadProcessor.php";
require_once "src/DataProcessor.php";
require_once "src/MuBench/Detector.php";
require_once "src/MuBench/Misuse.php";
require_once "src/MuBench/Review.php";
require_once "DatabaseTestCase.php";

use MuBench\Misuse;
use MuBench\Review;

class StoreReviewTest extends DatabaseTestCase
{

    function test_store_review()
    {
        $queryBuilder = new QueryBuilder($this->pdo, $this->logger);
        $upload_processor = new UploadProcessor($this->db, $queryBuilder, $this->logger);
        $data_processor = new DataProcessor($this->db, $this->logger);

        $data = [
            'review_name' => '-reviewer-',
            'review_exp' => 'ex1',
            'review_detector' => '-d-',
            'review_project' => '-p-',
            'review_version' => '-v-',
            'review_misuse' => '-m-',
            'review_comment' => '-comment-',
            'review_hit' => [
                0 => [
                    'hit' => 'Yes',
                    'types' => [
                        'missing/call'
                    ]
                ]
            ]
        ];


        $metadata = json_decode($this->metadata_json);
        $finding = json_decode($this->finding_json);

        $upload_processor->processData('ex1', $finding, $finding->{'potential_hits'});
        $upload_processor->processMetaData($metadata);
        $upload_processor->processReview($data);

        $detector = $data_processor->getDetector('-d-');
        $runs = $data_processor->getRuns($detector, 'ex1');

        $expected_run = [
            "exp" => "ex1",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "detector" => "detector_1",
            "misuses" => [
                new Misuse(
                    [
                    "misuse" => "-m-",
                    'project' => '-p-',
                    'version' => '-v-',
                    'description' => '-desc-',
                    'fix_description' => '-fix-desc-',
                    'violation_types' => 'superfluous/condition/null_check',
                    'file' => '-f-',
                    'method' => '-method-',
                    'diff_url' => '-diff-',
                    'snippets' => [0 => ['line' => '273', 'snippet' => '-code-']],
                    'patterns' => [0 => ['name' => '-p-id-', 'code' => '-pattern-code-','line' => '1']]
                    ],
                    [
                        [
                            'exp' => 'ex1',
                            'project' => '-p-',
                            'version' => '-v-',
                            'misuse' => '-m-',
                            'rank' => '0',
                            'custom1' => '-val1-',
                            'custom2' => '-val2-'
                        ]
                    ],
                    [
                        new Review([
                            'name' => '-reviewer-',
                            'exp' => 'ex1',
                            'detector' => '-d-',
                            'project' => '-p-',
                            'version' => '-v-',
                            'misuse' => '-m-',
                            'comment' => '-comment-',
                            'id' => '1',
                            'finding_reviews' => [
                                [
                                    'decision' => 'Yes',
                                    'id' => '1',
                                    'rank' => '0',
                                    'review' => '1',
                                    'violation_types' => [
                                        'missing/call'
                                    ]
                                ]
                            ]
                        ])
                    ])
            ]
        ];

        self::assertEquals([$expected_run], $runs);
    }

}
