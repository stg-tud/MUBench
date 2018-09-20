<?php

namespace MuBench\ReviewSite\Controllers;


use Illuminate\Database\Eloquent\Collection;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\FindingReview;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\Run;
use MuBench\ReviewSite\Models\Tag;
use MuBench\ReviewSite\Models\Violation;
use Slim\Http\Request;
use Slim\Http\Response;

class ReviewsController extends Controller
{
    public function getReview(Request $request, Response $response, array $args)
    {
        $experiment_id = $args['experiment_id'];
        $detector_muid = $args['detector_muid'];
        $project_muid = $args['project_muid'];
        $version_muid = $args['version_muid'];
        $misuse_muid = $args['misuse_muid'];

        $experiment = Experiment::find($experiment_id);
        $detector = Detector::findByIdOrName($detector_muid);
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->settings['default_ex2_review_size']);

        $reviewer = $this->user;
        if(array_key_exists('reviewer_name', $args)){
            $reviewer = Reviewer::findByIdOrName($args['reviewer_name']);
        }

        $resolution_reviewer = Reviewer::where(['name' => 'resolution'])->first();
        $is_reviewer = ($this->user && $reviewer && $this->user->id == $reviewer->id) || ($reviewer && $reviewer->id == $resolution_reviewer->id);

        $runs = Run::of($detector)->in($experiment)->orderBy('project_muid')->orderBy('version_muid')->get();

        list($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse) =
            $this->determineNavigationTargets($runs, $experiment, $project_muid, $version_muid, $misuse_muid, $reviewer, $ex2_review_size);

        $all_violations = Violation::all();
        $all_tags = Tag::all()->sortBy('name');
        $review = $misuse->getReview($reviewer);
        return $this->renderer->render($response, 'review.phtml', ['reviewer' => $reviewer, 'is_reviewer' => $is_reviewer,
            'misuse' => $misuse, 'experiment' => $experiment,
            'detector' => $detector, 'review' => $review,
            'violations' => $all_violations, 'tags' => $all_tags, 'next_misuse' => $next_misuse, 'previous_misuse' => $previous_misuse, 'next_reviewable_misuse' => $next_reviewable_misuse]);
    }

    public function getTodo(Request $request, Response $response, array $args)
    {
        $experiment_id = $args['experiment_id'];
        $reviewer_name = $args['reviewer_name'];

        $experiment = Experiment::find($experiment_id);
        $reviewer = Reviewer::findByIdOrName($reviewer_name);

        $detectors = Detector::withFindings($experiment);

        $open_misuses = [];
        foreach($detectors as $detector){
            $runs = RunsController::getRuns($detector, $experiment, $this->settings['default_ex2_review_size']);
            foreach($runs as $run){
                foreach($run->misuses as $misuse) {
                    /** @var Misuse $misuse */
                    if (!$misuse->hasReviewed($reviewer) && !$misuse->hasSufficientReviews() && sizeof($misuse->findings) > 0) {
                        $open_misuses[$detector->muid][] = $misuse;
                    }
                }
            }

        }
        return $this->renderer->render($response, 'todo.phtml', ['open_misuses' => $open_misuses, 'experiment' => $experiment]);
    }

    public function getOverview(Request $request, Response $response, array $args)
    {
        $experiment_id = $args['experiment_id'];
        $reviewer_name = $args['reviewer_name'];

        $experiment = Experiment::find($experiment_id);
        $reviewer = Reviewer::findByIdOrName($reviewer_name);

        $detectors = Detector::withFindings($experiment);

        $closed_misuses = [];
        foreach($detectors as $detector){
            $runs = Run::of($detector)->in($experiment)->get();
            foreach($runs as $run){
                foreach($run->misuses as $misuse){
                    /** @var Misuse $misuse */
                    if($misuse->hasReviewed($reviewer)){
                        $closed_misuses[$detector->muid][] = $misuse;
                    }
                }
            }

        }
        return $this->renderer->render($response, 'overview.phtml', ['closed_misuses' => $closed_misuses, 'experiment' => $experiment]);
    }

    public function postReview(Request $request, Response $response, array $args)
    {
        $review = $request->getParsedBody();

        $experiment_id = $args['experiment_id'];
        $detector_muid = $args['detector_muid'];
        $project_muid = $args['project_muid'];
        $version_muid = $args['version_muid'];
        $misuse_muid = $args['misuse_muid'];
        $comment = $review['review_comment'];
        $misuse_id = $review['misuse_id'];
        $hits = $review['review_hit'];
        $tags = array_key_exists('review_tags', $review) ? $review['review_tags'] : array();

        $reviewer_name = $args['reviewer_name'];
        $reviewer = Reviewer::findByIdOrName($reviewer_name);
        $this->updateOrCreateReview($misuse_id, $reviewer->id, $comment, $hits, $tags);

        if ($review["origin"] != "") {
            return $response->withRedirect("{$review["origin"]}");
        }else {
            $path = $this->router->pathFor("private.review", ["experiment_id" => $experiment_id,
                "detector_muid" => $detector_muid, "project_muid" => $project_muid, "version_muid" => $version_muid,
                "misuse_muid" => $misuse_muid, "reviewer_name" => $reviewer_name]);
            if(array_key_exists("origin_param", $review)){
                $path = $path . "?origin={$review["origin_param"]}";
            }
            return $response->withRedirect($path);
        }
    }

    public function updateOrCreateReview($misuse_id, $reviewer_id, $comment, $findings_reviews_by_rank, $tags)
    {
        $review = Review::firstOrNew(['misuse_id' => $misuse_id, 'reviewer_id' => $reviewer_id]);
        $review->comment = $comment;
        $review->save();
        TagsController::syncReviewTags($review->id, $tags);
        foreach ($findings_reviews_by_rank as $rank => $findings_review) {
            $findingReview = FindingReview::firstOrNew(['review_id' => $review->id, 'rank' => $rank]);
            $findingReview->decision = $findings_review['hit'];
            $findingReview->save();
            $findingReview->violations()->sync($findings_review['violations']);
        }
    }

    function determineNavigationTargets(Collection $runs, $experiment, $project_muid, $version_muid, $misuse_muid, $reviewer, $ex2_review_size)
    {
        $previous_misuse = NULL;
        $misuse = NULL;
        $next_misuse = NULL;
        $next_reviewable_misuse = NULL;
        $last_run = $runs->last();

        foreach ($runs as $run) {
            if ($misuse && !$next_misuse) {
                $next_misuse = $run->getMisuses($experiment, $ex2_review_size)->first();
            }
            if (!$misuse && $run->project_muid == $project_muid && $run->version_muid == $version_muid) {
                $this->findMisuse($run->getMisuses($experiment, $ex2_review_size), $misuse_muid, $reviewer, $previous_misuse, $misuse, $next_misuse, $next_reviewable_misuse);
                if($misuse && !$previous_misuse){
                    $previous_misuse = $last_run->getMisuses($experiment, $ex2_review_size)->last();
                }
                if(!$misuse){
                    // search for misuse out of review scope
                    foreach($run->misuses as $current_misuse){
                        if($current_misuse->misuse_muid == $misuse_muid){
                            $misuse = $current_misuse;
                            break;
                        }
                        $previous_misuse = $current_misuse;
                    }
                }
            } elseif ($misuse && !$next_reviewable_misuse) {
                $next_reviewable_misuse = $this->findNextReviewableMisuse($run->getMisuses($experiment, $ex2_review_size), $reviewer);
            }

            if ($next_misuse && $next_reviewable_misuse) {
                break;
            }
            $last_run = $run;
        }
        if ($misuse && !$next_misuse) {
            $next_misuse = $runs->first()->getMisuses($experiment, $ex2_review_size)->first();
        }
        if(!$next_reviewable_misuse){
            $next_reviewable_misuse = $this->findNextReviewableBeforeMisuse($runs, $experiment, $project_muid, $version_muid, $misuse, $reviewer, $ex2_review_size);
        }
        if(!$previous_misuse){
            $previous_misuse = $this->findPreviousMisuse($runs, $misuse);
        }
        return array($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse);
    }

    private function findMisuse(Collection $misuses, $misuse_muid, $reviewer, &$previous_misuse, &$misuse, &$next_misuse, &$next_reviewable_misuse)
    {
        foreach ($misuses as $current_misuse) {
            if ($misuse && !$next_misuse) {
                $next_misuse = $current_misuse;
            }
            if ($misuse && !$current_misuse->hasReviewed($reviewer) && !$current_misuse->hasSufficientReviews()) {
                $next_reviewable_misuse = $current_misuse;
                break;
            }
            if (!$misuse && $current_misuse->misuse_muid == $misuse_muid) {
                $misuse = $current_misuse;

            }
            if (!$misuse) {
                $previous_misuse = $current_misuse;
            }
        }
    }

    private function findPreviousMisuse(Collection $runs, $misuse)
    {
        $previous_misuse = NULL;
        $idx = sizeof($runs) - 1;
        while(!$previous_misuse && $idx >= 0){
            $run = $runs->get($idx);
            $previous_misuse = $run->misuses->last();
            if($previous_misuse && ($misuse->id == $previous_misuse->id)){
                $previous_misuse = NULL;
            }
            $idx--;
        }
        return $previous_misuse;
    }

    private function findNextReviewableMisuse(Collection $misuses, $reviewer)
    {
        $next_reviewable_misuse = NULL;
        foreach ($misuses as $current_misuse) {
            if (!$current_misuse->hasReviewed($reviewer) && !$current_misuse->hasSufficientReviews()) {
                $next_reviewable_misuse = $current_misuse;
                break;
            }
        }
        return $next_reviewable_misuse;
    }

    private function findNextReviewableBeforeMisuse(Collection $runs, $experiment, $project_muid, $version_muid, $misuse, $reviewer, $ex2_review_size)
    {
        $next_reviewable_misuse = NULL;
        foreach($runs as $run){
            $next_reviewable_misuse = $this->findNextReviewableMisuse($run->getMisuses($experiment, $ex2_review_size), $reviewer);

            if($run->project_muid == $project_muid && $run->version_muid == $version_muid){
                break;
            }
        }
        if($next_reviewable_misuse && $misuse->id == $next_reviewable_misuse->id) {
            return NULL;
        }
        return $next_reviewable_misuse;
    }

}
