<?php

require_once "DatabaseTestCase.php";

use MuBench\ReviewSite\Controller\FindingsUploader;
use MuBench\ReviewSite\Controller\ReviewUploader;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\Review;

class MisuseFilterTest extends DatabaseTestCase
{
    private $request_body;

    private $undecided_review = [
        'review_name' => 'reviewer1',
        'review_exp' => 'ex2',
        'review_detector' => '-d-',
        'review_project' => '-p-',
        'review_version' => '-v-',
        'review_misuse' => 1,
        'review_comment' => '-comment-',
        'review_hit' => [
            0 => [
                'hit' => '?',
                'types' => [
                    'missing/call'
                ]
            ]
        ]
    ];

    private $decided_review = [
        'review_name' => 'reviewer2',
        'review_exp' => 'ex2',
        'review_detector' => '-d-',
        'review_project' => '-p-',
        'review_version' => '-v-',
        'review_misuse' => 1,
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
            "potential_hits" => [
                [
                    "misuse" => "-m1-",
                    "rank" => 0,
                    "target_snippets" => [
                        ["first_line_number" => 5, "code" => "-code-"]
                    ],
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ],
                [
                    "misuse" => "-m2-",
                    "rank" => 1,
                    "target_snippets" => [
                        ["first_line_number" => 5, "code" => "-code-"]
                    ],
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ],
                [
                    "misuse" => "-m3-",
                    "rank" => 2,
                    "target_snippets" => [
                        ["first_line_number" => 5, "code" => "-code-"]
                    ],
                    "custom1" => "-val1-",
                    "custom2" => "-val2-"
                ]]
        ];

    }

    function test_no_reviews()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);

        $data = json_decode(json_encode($this->request_body));
        $uploader->processData("ex2", $data);
        $detector = $this->db->getOrCreateDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex2", 2);

        $expected_run = [
            "exp" => "ex2",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "detector" => $detector->id,
            "misuses" => [
                new Misuse(
                    ["misuse" => "0", "snippets" => [0 => ["line" => "5", "snippet" => "-code-", "id" => "1"]]],
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
                ),
                new Misuse(
                    ["misuse" => "1", "snippets" => [0 => ["line" => "5", "snippet" => "-code-", "id" => "2"]]],
                    [0 => [
                        "exp" => "ex2",
                        "project" => "-p-",
                        "version" => "-v-",
                        "misuse" => "1",
                        "rank" => "1",
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

    function test_one_unconclusive_reviews()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);
        $review_uploader = new ReviewUploader($this->db, $this->logger);
        $data = json_decode(json_encode($this->request_body));

        $uploader->processData("ex2", $data);
        $review_uploader->processReview($this->decided_review);
        $review_uploader->processReview($this->undecided_review);

        $detector = $this->db->getOrCreateDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex2", 2);


        self::assertEquals(3, sizeof($runs[0]['misuses']));
    }

    function test_conclusive_reviews()
    {
        $uploader = new FindingsUploader($this->db, $this->logger);
        $review_uploader = new ReviewUploader($this->db, $this->logger);
        $data = json_decode(json_encode($this->request_body));

        $uploader->processData("ex2", $data);
        $review_uploader->processReview($this->decided_review);
        $decided_reviewer2 = $this->undecided_review;
        $decided_reviewer2["review_hit"][0]["hit"] = "Yes";
        $review_uploader->processReview($decided_reviewer2);

        $detector = $this->db->getOrCreateDetector("-d-");
        $runs = $this->db->getRuns($detector, "ex2", 2);


        self::assertEquals(2, sizeof($runs[0]['misuses']));
    }

}
