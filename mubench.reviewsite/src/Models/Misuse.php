<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Collection;
use Illuminate\Database\Eloquent\Model;

class Misuse extends Model
{
    protected $fillable = ['misuse_muid', 'run_id', 'detector_id', 'metadata_id'];

    public function metadata()
    {
        return $this->belongsTo(Metadata::class);
    }

    public function reviews()
    {
        return $this->hasMany(Review::class);
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
        $snippets = Snippet::of($this->getProject(), $this->getVersion(), $this->misuse_muid, $this->getFile())
            ->where('detector_muid', $this->detector->muid)->orWhereNull('detector_muid')->get();
        $finding_lines = $this->findings->map(function ($finding) {
            return intval($finding['startline']);
        })->toArray();
        if($this->metadata && $this->metadata->line != -1){
            $finding_lines[] = $this->metadata->line;
        }
        if(count($finding_lines) == 0){
            return $snippets;
        }
        $fitting_snippets = new Collection;
        foreach($snippets as $snippet){
            $snippet_lines = count(preg_split('/\n/', $snippet->snippet));
            $last_line = $snippet->line + $snippet_lines;
            if($snippet->line <= min($finding_lines) && $last_line >= max($finding_lines)){
                $fitting_snippets[] = $snippet;
            }
        }
        if(count($fitting_snippets) == 0){
            return $snippets;
        }

        return $fitting_snippets;
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

    public function getViolations()
    {
        if($this->metadata){
           return $this->metadata->violations;
        }
        return new Collection;
    }

    public function getReviews()
    {
        return $this->reviews->filter(function($review){
            return $review->reviewer->name !== "resolution";
        });
    }

    public function hasSufficientReviews($number_of_required_reviews)
    {
        return $this->getReviewState($number_of_required_reviews) > ReviewState::NEEDS_REVIEW;
    }

    public function getNumberOfRequiredReviews($default_required_reviews)
    {
        return $default_required_reviews - sizeof($this->getReviews());
    }

    public function hasConclusiveReviewState($number_of_required_reviews)
    {
        $review_state = $this->getReviewState($number_of_required_reviews);
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

    public function hasViolations()
    {
        return !empty($this->getViolations());
    }

    public function hasSnippets(){
        return sizeof($this->snippets()) > 0;
    }

    public function getReviewState($number_of_required_reviews)
    {
        if (!$this->hasPotentialHits()) {
            return ReviewState::NOTHING_TO_REVIEW;
        } elseif (sizeof($this->reviews) < $number_of_required_reviews) {
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

    public function getTags($default_required_reviews)
    {
        if(!$this->hasConclusiveReviewState($default_required_reviews)){
            return new Collection;
        }else{
            $tags = new Collection;
            foreach($this->reviews as $review){
                $tags = $tags->merge($review->tags);
            }
            return $tags->unique('id');
        }
    }

}
