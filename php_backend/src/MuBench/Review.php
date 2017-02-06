<?php

namespace MuBench;


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
}