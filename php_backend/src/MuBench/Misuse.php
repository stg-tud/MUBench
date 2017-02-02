<?php

namespace MuBench;


use Prophecy\Exception\Doubler\MethodNotFoundException;

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
}
