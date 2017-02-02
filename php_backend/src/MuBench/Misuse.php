<?php

namespace MuBench;


use Prophecy\Exception\Doubler\MethodNotFoundException;

class ReviewState {
    const NOTHING_TO_REVIEW = 0;
    const NEEDS_REVIEW = 1;
    const AGREEMENT = 2;
    const DISAGREEMENT = 3;
    const RESOLVED = 4;
}

class Decision {
    const NO = 0;
    const MAYBE = 1;
    const YES = 2;
}

class Misuse
{
    public $id;

    private $data;
    private $potential_hits;
    private $reviews;

    public function __construct(array $data, array $potential_hits, array $reviews)
    {
        assert(array_key_exists("misuse", $data), "misuse requires id");

        $this->id = $data["misuse"];
        $this->data = $data;
        $this->potential_hits = $potential_hits;
        $this->reviews = $reviews;
    }

    public function getShortId()
    {
        $project = $this->data["project"];
        return substr($this->id, 0, strlen($project)) === $project ? substr($this->id, strlen($project) + 1) : $this->id;
    }

    public function getViolationTypes()
    {
        return explode(";", $this->data["violation_types"]);
    }

    public function hasPotentialHits()
    {
        return !empty($this->getPotentialHits());
    }

    public function getPotentialHits()
    {
        return $this->potential_hits;
    }

    public function hasReviewed($reviewer_name)
    {
        foreach ($this->reviews as $review) {
            if (strcmp($review["name"], $reviewer_name) === 0) return true;
        }
        return false;
    }

    public function getReviews()
    {
        return $this->reviews;
    }

    public function hasSufficientReviews()
    {
        return count($this->getReviews()) >= 2;
    }

    public function getReviewState()
    {
        if (!$this->hasPotentialHits()) {
            return ReviewState::NOTHING_TO_REVIEW;
        } else if (count($this->getReviews()) < 2) {
            return ReviewState::NEEDS_REVIEW;
        } else {
            $decisions = [];
            foreach ($this->getReviews() as $review) {
                $decision = self::getDecision($review);
                $decisions[$decision] = true;
            }
            if (count($decisions) > 1) {
                return ReviewState::DISAGREEMENT;
            } else {
                return ReviewState::AGREEMENT;
            }
        }
    }

    private static function getDecision($review)
    {
        $decision = Decision::NO;
        foreach ($review["finding_reviews"] as $finding_review) {
            if (strcmp($finding_review["decision"], "Yes") === 0) {
                $decision = Decision::YES;
                break;
            } else if (strcmp($finding_review["decision"], "Yes") === 0) {
                $decision = Decision::MAYBE;
            }
        }
        return $decision;
    }
}
