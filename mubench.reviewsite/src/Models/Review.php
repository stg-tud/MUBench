<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Review extends Model
{

    protected $fillable = ['misuse_id', 'reviewer_id'];

    public function reviewer()
    {
        return $this->belongsTo(Reviewer::class);
    }

    public function finding_reviews()
    {
        return $this->hasMany(FindingReview::class);
    }

    public function getDecision()
    {
        $decision = Decision::NO;
        foreach ($this->finding_reviews as $finding_review) {
            if (strcmp($finding_review->decision, "Yes") === 0) {
                $decision = Decision::YES;
                break;
            } else if (strcmp($finding_review->decision, "?") === 0) {
                $decision = Decision::MAYBE;
            }
        }
        return $decision;
    }

    public function hasHitViolationTypes($rank){
        return !empty($this->getHitViolationTypes($rank));
    }

    public function getHitDecision($rank){
        return $this->getFindingReviews($rank)->decision;
    }

    public function getHitViolationTypes($rank){
        return $this->getFindingReviews($rank)->violation_types->toArray();
    }

    public function identifiesHit()
    {
        return $this->getDecision() == Decision::YES;
    }

    public function getLowestHitRank()
    {
        foreach($this->finding_reviews as $finding_review)
        {
            if(strcmp($finding_review->decision, "Yes") === 0){
                return $finding_review->rank;
            }
        }
        throw new \RuntimeException("no hit was identified");
    }

    private function getFindingReviews($rank){
        return $this->finding_reviews->where('rank', $rank)->first();
    }
}
