<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;
use MuBench\ReviewSite\Model\Detector;

class ReviewUploader
{

    private $db;
    private $logger;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
        $this->logger = $logger;
    }

    public function processReview($review)
    {
        $name = $review['review_name'];
        $exp = $review['review_exp'];
        $detector = $this->db->getOrCreateDetector($review['review_detector']);
        $project = $review['review_project'];
        $version = $review['review_version'];
        $misuse = $review['review_misuse'];
        $comment = $review['review_comment'];
        $hits = $review['review_hit'];

        $this->deleteExistingReview($exp, $detector, $project, $version, $misuse, $name);
        $this->saveReview($exp, $detector, $project, $version, $misuse, $name, $comment, $hits);
    }

    private function deleteExistingReview($exp, Detector $detector, $project, $version, $misuse, $name)
    {
        $review = $this->db->getReview($exp, $detector, $project, $version, $misuse, $name);
        if ($review) {
            $reviewId = intval($review['id']);
            $this->db->table('reviews')->where('id', $reviewId)->delete();
            foreach ($this->db->getReviewFindings($reviewId) as $finding) {
                $findingId = intval($finding['id']);
                $this->db->table('review_findings')->where('id', $findingId)->delete();
                $this->db->table('review_findings_types')->where('review_finding', $findingId)->delete();
            }
        }
    }

    private function saveReview($exp, Detector $detector, $project, $version, $misuse, $name, $comment, $hits)
    {
        $reviewId = $this->db->table('reviews')->insert(['exp' => $exp,'detector' => $detector->id,
            'project' => $project, 'version' => $version, 'misuse' => $misuse, 'name' => $name, 'comment' => $comment]);
        foreach ($hits as $key => $hit) {
            $findingId = $this->db->table('review_findings')->insert(['review' => $reviewId, 'rank' => $key, 'decision' => $hit['hit']]);
            foreach ($hit['types'] as $type) {
                $typeId = $this->db->getTypeIdByName($type);
                $this->db->table('review_findings_types')->insert(['review_finding' => $findingId, 'type' => $typeId]);
            }
        }
    }
}