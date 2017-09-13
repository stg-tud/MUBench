<?php

namespace MuBench\ReviewSite\Controller;

require_once 'DatabaseTestCase.php';

use DatabaseTestCase;
use MuBench\ReviewSite\Model\Decision;
use MuBench\ReviewSite\Model\Detector;
use MuBench\ReviewSite\Model\Review;
use MuBench\ReviewSite\Model\Misuse;
use Slim\Views\PhpRenderer;

class ReviewControllerTest extends DatabaseTestCase
{
    private $detector;

    /**
     * @var ReviewController $reviewController
     */
    private $reviewController;

    function setUp()
    {
        parent::setUp();
        $this->detector = $this->db->getOrCreateDetector('-d-');
        $metadataController = new MetadataController($this->db, $this->logger);
        $renderer = new PhpRenderer();
        $this->reviewController = new ReviewController('', '', $this->db, $renderer, $metadataController);
    }


    function test_store_review()
    {
        $this->reviewController->updateReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-', '-comment-', [['hit' => 'Yes']]);

        $review = $this->reviewController->getReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-');

        self::assertEquals(new Review([
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
                    'violation_types' => []
                ]
            ]
        ]), $review);
    }

    function test_update_review()
    {
        $this->reviewController->updateReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-', '-comment-', [['hit' => 'Yes']]);
        $this->reviewController->updateReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-', '-comment-', [['hit' => 'No']]);

        $review = $this->reviewController->getReview('ex1', $this->detector, '-p-', '-v-', '-m-', '-reviewer-');

        $decision = $review->getDecision();
        self::assertEquals(Decision::NO, $decision);
    }

    function test_stores_violation_types()
    {
        $this->reviewController->updateReview('ex2', $this->detector, '-p-', '-v-', '-m-', '-reviewer-', '-comment-', [['hit' => 'Yes', 'types' => ['1']]]);

        $review = $this->reviewController->getReview('ex2', $this->detector, '-p-', '-v-', '-m-', '-reviewer-');

        $actualTypes = $review->getHitViolationTypes(0);
        self::assertEquals(["missing/call"], $actualTypes);
    }

    function test_get_misuse_ex1()
    {
        $finding = [
            "detector" => "-d-",
            "project" => "-p-",
            "version" => "-v-",
            "potential_hits" => [
                [
                    "misuse" => "-m-",
                    "rank" => 0,
                    "target_snippets" => [],
                ]
            ]
        ];

        $detector = new Detector('-d-', 1);
        $metadataController = new MetadataController($this->db, $this->logger);
        $metadataController->updateMetadata('-p-', '-v-', '-m-', '-desc-', [
            'description' => '-fix-desc-',
            'diff-url' => '-diff-'
        ], [
            "file" => "-f-",
            "method" => "-method-"
        ], ["superfluous/condition/null_check"], [
            [
                "snippet" => [
                    "first_line" => 1,
                    "code" => "-pattern-code-",

                ],
                "id" => "-p-id-"
            ]
        ], [[
            'code' => '-code-',
            'first_line_number' => 273
        ]]);
        $findingUploader = new FindingsUploader($this->db, $this->logger);
        $findingUploader->processData('ex1', json_decode(json_encode($finding)));

        $actualMisuse = $this->reviewController->getMisuse('ex1', $detector, '-p-', '-v-', '-m-');

        $expectedMisuse = new Misuse(
            [
                'misuse' => '-m-',
                'project' => '-p-',
                'version' => '-v-',
                'description' => '-desc-',
                'fix_description' => '-fix-desc-',
                'file' => '-f-',
                'method' => '-method-',
                'diff_url' => '-diff-',
                'violation_types' => ['superfluous/condition/null_check'],
                'patterns' =>
                    [[
                        'name' => '-p-id-',
                        'code' => '-pattern-code-',
                        'line' => '1'
                    ]],
                'snippets' =>
                    [[
                        'line' => '273',
                        'snippet' => '-code-'
                    ]],
                'tags' => []
            ],
            [
                [
                    'exp' => 'ex1',
                    'project' => '-p-',
                    'version' => '-v-',
                    'misuse' => '-m-',
                    'rank' => '0'
                ]
            ], []);

        self::assertEquals($expectedMisuse, $actualMisuse);
    }

    function test_get_misuse_ex2()
    {
        $finding = [
        "detector" => "-d-",
            "project" => "-p-",
            "version" => "-v-",
            "potential_hits" => [
            [
                "rank" => 0,
                "target_snippets" => [],
            ]
        ]
        ];
        $detector = new Detector('-d-', 1);
        $findingUploader = new FindingsUploader($this->db, $this->logger);
        $findingUploader->processData('ex2', json_decode(json_encode($finding)));

        $actualMisuse = $this->reviewController->getMisuse('ex2', $detector, '-p-', '-v-', 0);

        $expectedMisuse = new Misuse(
            [
                'project' => '-p-',
                'version' => '-v-',
                'misuse' => 0,
                'snippets' => [],
                'tags' => []
            ],
            [
                [
                    'exp' => 'ex2',
                    'project' => '-p-',
                    'version' => '-v-',
                    'misuse' => 0,
                    'rank' => 0
                ]
            ], []);
        self::assertEquals($expectedMisuse, $actualMisuse);
    }

}
