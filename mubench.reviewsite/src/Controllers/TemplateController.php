<?php
namespace MuBench\ReviewSite\Controllers;


use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\ReviewState;

class TemplateController extends Controller
{

    public function __construct($container)
    {
        parent::__construct($container);
    }

    public function getReviewStates($experiment, $detector, $ex2_review_size)
    {
        $review_states = [ReviewState::NEEDS_REVIEW => false, ReviewState::NEEDS_CLARIFICATION => false, ReviewState::DISAGREEMENT => false];
        $runs = RunsController::getRuns($detector, $experiment, $ex2_review_size);
        foreach ($runs as $run) {
            $this->getReviewStatesFromMisuses($run, $review_states);
            if(!in_array(false, $review_states, true)){
                break;
            }
        }
        return $review_states;
    }

    private function getReviewStatesFromMisuses($run, &$review_states)
    {
        foreach ($run->misuses as $misuse) {
            /** @var Misuse $misuse */
            if ($misuse->getReviewState() == ReviewState::NEEDS_REVIEW || $misuse->getReviewState() == ReviewState::NEEDS_CLARIFICATION || $misuse->getReviewState() == ReviewState::DISAGREEMENT) {
                $review_states[$misuse->getReviewState()] = True;
                if(!in_array(false, $review_states, true)){
                    return;
                }
            }
        }
    }

}