<?php

namespace MuBench\ReviewSite\Model;


abstract class RunsResult
{
    public $number_of_projects = 0;
    public $number_of_synthetics = 0;
    public $number_of_misuses = 0;
    public $misuses_to_review = 0;
    public $open_reviews = 0;
    public $number_of_needs_clarification = 0;

    public $yes_agreements = 0;
    public $no_agreements = 0;
    public $yes_no_disagreements = 0;
    public $no_yes_disagreements = 0;

    public $number_of_hits = 0;

    function __construct(array $runs)
    {
        $projects = array();
        $misuses = array();
        $synthetics = array();
        foreach ($runs as $run) {
            if (strcmp($run["project"], "synthetic") === 0) {
                $synthetics[$run["version"]] = 1;
            } else {
                $projects[$run["project"] . "." . $run["version"]] = 1;
            }

            foreach ($run["misuses"] as $misuse) { /** @var $misuse Misuse */
                $misuses[$run["project"] . "." . $misuse->id] = 1;
                if ($misuse->hasPotentialHits()) {
                    $this->misuses_to_review++;
                }
                $reviewState = $misuse->getReviewState();
                switch ($reviewState) {
                    case ReviewState::NEEDS_REVIEW:
                        $this->open_reviews += 2 - count($misuse->getReviews());
                        break;
                    case ReviewState::AGREEMENT_YES:
                        $this->yes_agreements++;
                        $this->number_of_hits++;
                        break;
                    case ReviewState::AGREEMENT_NO:
                        $this->no_agreements++;
                        break;
                    case ReviewState::NEEDS_CLARIFICATION:
                        $this->number_of_needs_clarification++;
                        break;
                    case ReviewState::DISAGREEMENT:
                    case ReviewState::RESOLVED_NO:
                    case ReviewState::RESOLVED_YES:
                        if (current($misuse->getReviews())->getDecision() == Decision::YES) {
                            $this->yes_no_disagreements++;
                        } else {
                            $this->no_yes_disagreements++;
                        }
                        if ($reviewState == ReviewState::RESOLVED_YES) {
                            $this->number_of_hits++;
                        }
                        break;
                }
            }
        }
        $this->number_of_projects = count($projects);
        $this->number_of_synthetics = count($synthetics);
        $this->number_of_misuses = count($misuses);
    }

    abstract public function getDisplayName();

    public function getNumberOfAgreements()
    {
        return $this->yes_agreements + $this->no_agreements;
    }

    public function getNumberOfDisagreements()
    {
        return $this->yes_no_disagreements + $this->no_yes_disagreements;
    }

    public function getKappaScore()
    {
        $p0 = $this->getKappaP0();
        $pe = $this->getKappaPe();
        return ($p0 - $pe) / (1 - $pe);
    }

    public function getKappaP0()
    {
        return $this->getNumberOfAgreements() / $this->misuses_to_review;
    }

    public function getKappaPe()
    {
        $yes_faction = $this->yes_agreements / $this->misuses_to_review;
        $no_fraction = $this->no_agreements / $this->misuses_to_review;
        $yes_no_fraction = $this->yes_no_disagreements / $this->misuses_to_review;
        $no_yes_fraction = $this->no_yes_disagreements / $this->misuses_to_review;
        return ($yes_faction * $no_fraction) + ($yes_no_fraction * $no_yes_fraction);
    }

    public function getRecall()
    {
        return $this->number_of_hits / $this->number_of_misuses;
    }

    public function getPrecision()
    {
        return $this->number_of_hits / $this->misuses_to_review;
    }
}
