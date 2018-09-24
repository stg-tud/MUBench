<?php

namespace MuBench\ReviewSite\Models;

use Illuminate\Database\Eloquent\Collection;

class Run extends DetectorDependent
{
    protected  function getTableName(Detector $detector)
    {
        return 'runs_' . $detector->id;
    }

    public function misuses()
    {
        return $this->hasMany(Misuse::class, 'run_id', 'id')->where('detector_id', $this->detector->id);
    }

    public function getMisuses($experiment, $max_review_size)
    {
        $filtered_misuses = new Collection;
        $misuses = $this->misuses->sortBy('misuse_muid', SORT_NATURAL);
        if($experiment->id === 1) {
            foreach($misuses as $misuse){
                if($misuse->metadata && !$misuse->metadata->correct_usages->isEmpty()){
                    $filtered_misuses->add($misuse);
                }
            }
        } else if($experiment->id === 2) {
            $conclusive_reviews = 0;
            foreach ($misuses as $misuse) {
                if ($conclusive_reviews >= $max_review_size) {
                    break;
                }
                $filtered_misuses->add($misuse);
                if ($misuse->hasConclusiveReviewState() || (!$misuse->hasSufficientReviews() && !$misuse->hasInconclusiveReview())) {
                    $conclusive_reviews++;
                }
            }
        } else {
            foreach($misuses as $misuse){
                if($misuse->metadata){
                    $filtered_misuses->add($misuse);
                }
            }
        }
        return $filtered_misuses;
    }
}
