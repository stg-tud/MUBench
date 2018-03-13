<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Collection;
use Illuminate\Database\Eloquent\Model;

class Misuse extends Model
{
    const NUMBER_OF_REQUIRED_REVIEWS = 2;

    protected $fillable = ['misuse_muid', 'run_id', 'detector_id', 'metadata_id'];

    public function metadata()
    {
        return $this->belongsTo(Metadata::class);
    }

    public function reviews()
    {
        return $this->hasMany(Review::class);
    }

    public function misuse_tags()
    {
        return $this->belongsToMany(Tag::class, 'misuse_tags', 'misuse_id', 'tag_id');
    }

    public function detector()
    {
        return $this->belongsTo(Detector::class, 'detector_id', 'id');
    }

    public function run()
    {
        return $this->belongsTo(Run::class);
    }

    public function findings()
    {
        return $this->hasMany(Finding::class)->orderBy('rank');
    }

    public function snippets()
    {
        return Snippet::of($this->getProject(), $this->getVersion(), $this->misuse_muid, $this->getFile())->get();
    }

    public function getFile()
    {
        if($this->metadata){
            return $this->metadata->file;
        }
        return $this->findings[0]->file;
    }

    public function getMethod()
    {
        if($this->metadata){
            return $this->metadata->method;
        }
        return $this->findings[0]->method;
    }

    public function getProject()
    {
        return $this->run->project_muid;
    }

    public function getVersion()
    {
        return $this->run->version_muid;
    }

    protected function newRelatedInstance($class)
    {
        $instance = parent::newRelatedInstance($class);
        if ($class == Run::class || $class == Finding::class) {
            $instance->setDetector($this->detector);
        }
        return $instance;
    }

    public function getViolationTypes()
    {
        if($this->metadata){
           return $this->metadata->violation_types;
        }
        return new Collection;
    }

    public function getReviews()
    {
        return $this->reviews->filter(function($review){
            return $review->reviewer->name !== "resolution";
        });
    }

    public function hasSufficientReviews()
    {
        return $this->getReviewState() > ReviewState::NEEDS_REVIEW;
    }

    public function getNumberOfRequiredReviews()
    {
        return self::NUMBER_OF_REQUIRED_REVIEWS - sizeof($this->getReviews());
    }

    public function hasConclusiveReviewState()
    {
        $review_state = $this->getReviewState();
        return $review_state != ReviewState::NEEDS_REVIEW && $review_state != ReviewState::DISAGREEMENT && $review_state != ReviewState::NEEDS_CLARIFICATION && $review_state != ReviewState::UNRESOLVED;
    }

    public function hasInconclusiveReview()
    {
        $decisions = $this->getReviewDecisions();
        if (array_key_exists(Decision::MAYBE, $decisions)) {
            return true;
        }
        return false;
    }

    public function hasViolationTypes()
    {
        return !empty($this->getViolationTypes());
    }

    public function hasSnippets(){
        return sizeof($this->snippets()) > 0;
    }

    public function getReviewState()
    {
        if (!$this->hasPotentialHits()) {
            return ReviewState::NOTHING_TO_REVIEW;
        } elseif (sizeof($this->reviews) < self::NUMBER_OF_REQUIRED_REVIEWS) {
            return ReviewState::NEEDS_REVIEW;
        } else {
            $byResolution = $this->hasResolutionReview();
            if ($byResolution) {
                $decision = $this->getResolutionReview()->getDecision();
                if ($decision == Decision::YES) {
                    return ReviewState::RESOLVED_YES;
                } elseif ($decision == Decision::NO) {
                    return ReviewState::RESOLVED_NO;
                } else {
                    return ReviewState::UNRESOLVED;
                }
            } else {
                $decisions = $this->getReviewDecisions();
                if (array_key_exists(Decision::MAYBE, $decisions)) {
                    return ReviewState::NEEDS_CLARIFICATION;
                } elseif (count($decisions) > 1) {
                    return ReviewState::DISAGREEMENT;
                } elseif (array_key_exists(Decision::YES, $decisions)) {
                    return ReviewState::AGREEMENT_YES;
                } else {
                    return ReviewState::AGREEMENT_NO;
                }
            }
        }
    }


    private function getReviewDecisions(){
        $decisions = [];
        foreach ($this->reviews as $review) {
            $decisions[$review->getDecision()] = true;
        }
        return $decisions;
    }

    public function hasResolutionReview()
    {
        return $this->getResolutionReview() !== null;
    }

    public function getReview($reviewer)
    {
        if(!$reviewer){
            return NULL;
        }
        foreach ($this->reviews as $review) {
            if ($review->reviewer->id == $reviewer->id) return $review;
        }
        return NULL;
    }

    public function getResolutionReview()
    {
        return $this->reviews->first(function ($value, $key) { return $value->reviewer->isResolutionReviewer(); });
    }

    public function hasPotentialHits()
    {
        return sizeof($this->findings) > 0;
    }

    public function hasReviewed($reviewer)
    {
        if($reviewer) {
            foreach ($this->reviews as $review) {
                if ($review->reviewer->id === $reviewer->id) {
                    return true;
                }
            }
        }
        return false;
    }

}
