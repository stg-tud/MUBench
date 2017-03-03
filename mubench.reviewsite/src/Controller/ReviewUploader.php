<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;

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
        $detector = $review['review_detector'];
        $project = $review['review_project'];
        $version = $review['review_version'];
        $misuse = $review['review_misuse'];
        $comment = $review['review_comment'];
        $hits = $review['review_hit'];
        $statements = [];
        $oldReview = $this->db->getReview($exp, $detector, $project, $version, $misuse, $name);
        if($oldReview){
            $oldId = intval($oldReview['id']);
            $oldFindings = $this->db->getReviewFindings($oldId);
            foreach($oldFindings as $oldFinding){
                $statements[] = $this->getReviewFindingsDeleteStatement(intval($oldFinding['id']));
                $statements[] = $this->getReviewFindingsTypeDelete(intval($oldFinding['id']));
            }
        }

        $statements[] = $this->getReviewDeleteStatement($exp, $detector, $project, $version, $misuse, $name);
        $statements[] = $this->getReviewStatement($exp, $detector, $project, $version, $misuse, $name, $comment);
        $this->db->execStatements($statements);
        $newReview = $this->db->getReview($exp, $detector, $project, $version, $misuse, $name);
        if(!$newReview){
            $this->logger->error("Review not found");
            return;
        }
        $id = intval($newReview['id']);
        foreach($hits as $key => $hit){
            $this->db->execStatement($this->getReviewFindingStatement($id, $hit['hit'], $key));
            $findingEntry = $this->db->getReviewFinding($id, $key);
            if(!$findingEntry){
                $this->logger->error("finding not found");
                continue;
            }
            $findingId = intval($findingEntry['id']);
            foreach($hit['types'] as $type){
                $typeId = $this->db->getTypeIdByName($type);
                $this->db->execStatement($this->addReviewType($findingId, $typeId));
            }
        }
    }

    private function getReviewFindingsDeleteStatement($findingId)
    {
        return "DELETE FROM review_findings WHERE id=" . $this->db->quote($findingId) . ";";
    }

    private function getReviewFindingsTypeDelete($id)
    {
        return "DELETE FROM review_findings_type WHERE review_finding=" . $this->db->quote($id) . ";";
    }

    private function getReviewDeleteStatement($exp, $detector, $project, $version, $misuse, $name)
    {
        return "DELETE FROM reviews WHERE exp=" .
            $this->db->quote($exp) .
            " AND detector=" .
            $this->db->quote($detector) .
            " AND project=" .
            $this->db->quote($project) .
            " AND version=" .
            $this->db->quote($version) .
            " AND misuse=" .
            $this->db->quote($misuse) .
            " AND name=" .
            $this->db->quote($name) .
            ";";
    }

    private function getReviewStatement($exp, $detector, $project, $version, $misuse, $name, $comment)
    {
        return "INSERT INTO reviews (exp, detector, project, version, misuse, name, comment) VALUES (" .
            $this->db->quote($exp) .
            "," .
            $this->db->quote($detector) .
            "," .
            $this->db->quote($project) .
            "," .
            $this->db->quote($version) .
            "," .
            $this->db->quote($misuse) .
            "," .
            $this->db->quote($name) .
            "," .
            $this->db->quote($comment) .
            ");";
    }

    private function getReviewFindingStatement($reviewId, $decision, $rank)
    {
        return "INSERT INTO review_findings (decision, review, rank) VALUES(" .
            $this->db->quote($decision) .
            ", " .
            $this->db->quote($reviewId) .
            "," .
            $this->db->quote($rank) .
            ");";
    }


    private function addReviewType($findingId, $type)
    {
        return "INSERT INTO review_findings_type (review_finding, type) VALUES (" .
            $this->db->quote($findingId) .
            "," .
            $this->db->quote($type) .
            ");";
    }

}