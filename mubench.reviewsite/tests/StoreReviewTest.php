<?php

require_once "DatabaseTestCase.php";

use MuBench\ReviewSite\Controller\FindingsUploader;
use MuBench\ReviewSite\Controller\MetadataUploader;
use MuBench\ReviewSite\Controller\ReviewUploader;
use MuBench\ReviewSite\Model\Decision;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\Review;

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
    private $detector;

    /**
     * @var ReviewUploader $review_uploader
     */
    private $review_uploader;

    function setUp()
    {
        parent::setUp();

        $this->detector = $this->db->getOrCreateDetector('-d-');
        $this->expected_run = [
            "exp" => "ex1",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "detector" => $this->detector->id,
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
                            'detector' => $this->detector->id,
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

        $finding_uploader->processData('ex1', $finding);
        $metadata_uploader->processMetaData($metadata);

        $this->review_uploader = new ReviewUploader($this->db, $this->logger);
    }


    function test_store_review()
    {
        $this->review_uploader->processReview($this->data);

        $runs = $this->db->getRuns($this->detector, 'ex1');

        self::assertEquals([$this->expected_run], $runs);
    }

    function test_update_review()
    {
        $this->review_uploader->processReview($this->data);
        $this->data['review_hit'][0]['hit'] = "No";
        $this->review_uploader->processReview($this->data);

        $runs = $this->db->getRuns($this->detector, 'ex1');
        /** @var Misuse $misuse */
        $misuse = $runs[0]["misuses"][0];
        $review = $misuse->getReview("-reviewer-");
        self::assertEquals($review->getDecision(), Decision::NO);
    }

}
