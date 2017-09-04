<?php

namespace MuBench\ReviewSite\Model;


class Review
{
    private $data;

    function __construct(array $data)
    {
        assert(array_key_exists("name", $data), "review requires name");

        $this->data = $data;
        usort($this->data["finding_reviews"], function($lhs, $rhs){ return intval($lhs['rank']) - intval($rhs['rank']);});
    }

    public function getId()
    {
        return $this->data["id"];
    }

    public function getReviewerName()
    {
        return $this->data["name"];
    }

    public function getDecision()
    {
        $decision = Decision::NO;
        foreach ($this->data["finding_reviews"] as $finding_review) {
            if (strcmp($finding_review["decision"], "Yes") === 0) {
                $decision = Decision::YES;
                break;
            } else if (strcmp($finding_review["decision"], "?") === 0) {
                $decision = Decision::MAYBE;
            }
        }
        return $decision;
    }

    public function hasHitViolationTypes($rank){
        return !empty($this->getHitViolationTypes($rank));
    }

    // REFACTOR should return a Decision
    public function getHitDecision($rank){
        return $this->getReviewFinding($rank)['decision'];
    }

    public function getHitViolationTypes($rank){
        return $this->getReviewFinding($rank)['violation_types'];
    }

    public function identifiesHit()
    {
        return $this->getDecision() == Decision::YES;
    }

    public function getLowestHitRank()
    {
        foreach($this->data["finding_reviews"] as $finding_review)
        {
            if(strcmp($finding_review["decision"], "Yes") === 0){
                return $finding_review["rank"];
            }
        }
        throw new \RuntimeException("no hit was identified");
    }

    // REFACTOR rename to findings reviews
    private function getReviewFinding($rank){
        foreach ($this->data["finding_reviews"] as $finding_review){
            if(strcmp($finding_review["rank"], $rank) == 0){
                return $finding_review;
            }
        }
        return null;
    }

    public function getFindingReviews()
    {
        return $this->data["finding_reviews"];
    }

    public function getComment()
    {
        return $this->data["comment"];
    }
}