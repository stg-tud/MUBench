<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Collection;
use Illuminate\Database\Eloquent\Model;

class Review extends Model
{

    protected $fillable = ['misuse_id', 'reviewer_id', 'comment'];

    public function reviewer()
    {
        return $this->belongsTo(Reviewer::class);
    }

    public function finding_reviews()
    {
        return $this->hasMany(FindingReview::class);
    }

    public function tags()
    {
        return $this->belongsToMany(Tag::class, 'review_tags', 'review_id', 'tag_id');
    }

    public function misuse()
    {
        return $this->belongsTo(Misuse::class);
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

    public function hasHitViolations($rank){
        return !empty($this->getHitViolations($rank));
    }

    public function getHitDecision($rank){
        return $this->getFindingReviews($rank)->decision;
    }

    public function getHitViolations($rank){
        return $this->getFindingReviews($rank)->violations->toArray();
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
