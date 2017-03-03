<?php

require_once "src/Upload/FindingsUploader.php";
require_once "src/Upload/MetadataUploader.php";
require_once "src/Upload/ReviewUploader.php";
require_once "src/MuBench/Detector.php";
require_once "src/MuBench/Misuse.php";
require_once "src/MuBench/Review.php";
require_once "DatabaseTestCase.php";

use MuBench\Misuse;
use MuBench\Review;

class StoreReviewTest extends DatabaseTestCase
{
    private $data = [
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

    private $expected_run;
    private $review_uploader;

    function setUp()
    {
        parent::setUp();

        $this->expected_run = [
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

        $finding_uploader = new FindingsUploader($this->db, $this->logger);
        $metadata_uploader = new MetadataUploader($this->db, $this->logger);

        $metadata = json_decode($this->metadata_json);
        $finding = json_decode($this->finding_json);

        $finding_uploader->processData('ex1', $finding, $finding->{'potential_hits'});
        $metadata_uploader->processMetaData($metadata);

        $this->review_uploader = new ReviewUploader($this->db, $this->logger);
    }


    function test_store_review()
    {
        $this->review_uploader->processReview($this->data);

        $detector = $this->db->getDetector('-d-');
        $runs = $this->db->getRuns($detector, 'ex1');
        self::assertEquals([$this->expected_run], $runs);
    }

    function test_update_review()
    {
        $this->review_uploader->processReview($this->data);
        $this->data['review_hit'][0]['hit'] = "No";
        $this->review_uploader->processReview($this->data);

        $detector = $this->db->getDetector('-d-');
        $runs = $this->db->getRuns($detector, 'ex1');
        $review = $runs[0]["misuses"][0]->getReview("-reviewer-");
        self::assertEquals($review->getDecision(), \MuBench\Decision::NO);
    }

}
