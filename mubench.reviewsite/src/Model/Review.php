<?php

namespace MuBench\ReviewSite\Model;


class Review
{
    private $data;

    function __construct(array $data)
    {
        assert(array_key_exists("name", $data), "review requires name");

        $this->data = $data;
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

    public function getHitDecision($rank){
        return $this->getReviewFinding($rank)['decision'];
    }

    public function getHitViolationTypes($rank){
        return $this->getReviewFinding($rank)['violation_types'];
    }

    private function getReviewFinding($rank){
        foreach ($this->data["finding_reviews"] as $finding_review){
            if(strcmp($finding_review["rank"], $rank) == 0){
                return $finding_review;
            }
        }
        return null;
    }

    public function getComment()
    {
        return $this->data["comment"];
    }
}