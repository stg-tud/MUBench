<?php
namespace MuBench\ReviewSite\Extensions;


use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\ReviewState;

class MenuViewExtension
{

    public function getReviewStates($experiment, $detector, $ex2_review_size, $user)
    {
        $review_states = [ReviewState::NEEDS_REVIEW => ['global' => false, 'personal' => false], ReviewState::NEEDS_CLARIFICATION => false, ReviewState::DISAGREEMENT => false];
        $runs = RunsController::getRuns($detector, $experiment, $ex2_review_size);
        foreach ($runs as $run) {
            $this->getReviewStatesFromMisuses($run, $review_states, $user);
            if(!in_array(false, $review_states, true) && !in_array(false, $review_states[ReviewState::NEEDS_REVIEW], true)){
                break;
            }
        }
        return $review_states;
    }

    private function getReviewStatesFromMisuses($run, &$review_states, $user)
    {
        foreach ($run->misuses as $misuse) {
            /** @var Misuse $misuse */
            if ($misuse->getReviewState() == ReviewState::NEEDS_REVIEW || $misuse->getReviewState() == ReviewState::NEEDS_CLARIFICATION || $misuse->getReviewState() == ReviewState::DISAGREEMENT) {
                if($misuse->getReviewState() == ReviewState::NEEDS_REVIEW){
                    $review_states[$misuse->getReviewState()]["global"] = true;
                    if(!$misuse->hasReviewed($user)){
                        $review_states[$misuse->getReviewState()]["personal"] = true;
                    }
                }else{
                    $review_states[$misuse->getReviewState()] = true;
                }
                if(!in_array(false, $review_states, true)){
                    return;
                }
            }
        }
    }

}