<?php

namespace MuBench\ReviewSite\Controllers;


use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\FindingReview;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\ReviewState;
use MuBench\ReviewSite\Models\Run;
use MuBench\ReviewSite\Models\Tag;
use MuBench\ReviewSite\Models\Type;
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
        $detector = Detector::find($detector_muid);
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->settings['default_ex2_review_size']);

        $reviewer = array_key_exists('reviewer_name', $args) ? Reviewer::where(['name' => $args['reviewer_name']])->first() : $this->user;
        $resolution_reviewer = Reviewer::where(['name' => 'resolution'])->first();
        $is_reviewer = ($this->user && $reviewer && $this->user->id == $reviewer->id) || ($reviewer && $reviewer->id == $resolution_reviewer->id);

        $runs = RunsController::getRuns($detector, $experiment, $ex2_review_size);
        $current_run = Run::of($detector)->in($experiment)->where(['project_muid' => $project_muid, 'version_muid' => $version_muid])->first();
        $current_misuse = $current_run->misuses()->where('misuse_muid', $misuse_muid)->first();

        $reviewable_runs_with_current = $runs->filter(function ($value, $key) use ($current_misuse) {
            if ($value->misuses->isNotEmpty() && $value->misuses->contains(function ($value, $key) use ($current_misuse) {
                    return $value->getReviewState() == ReviewState::NEEDS_REVIEW || $value->id == $current_misuse->id;
                })) {
                return True;
            }
            return False;
        });


        $previous_misuse = NULL;
        $next_misuse = NULL;
        $next_run = NULL;
        $previous_run = NULL;
        $current_misuses = $current_run->misuses->filter(function ($value, $key) use ($current_misuse) {
            return $value->getReviewState() == ReviewState::NEEDS_REVIEW || $value->id == $current_misuse->id;
        });
        if ($reviewable_runs_with_current->count() > 1 || ($reviewable_runs_with_current->count() == 1 && $current_misuses->count() > 1)) {
            $found = False;
            foreach ($current_misuses as $key => $misuse) {
                if ($found) {
                    $next_misuse = $misuse;
                    break;
                }
                if ($misuse->misuse_muid == $misuse_muid) {
                    $found = True;
                }
                if (!$found) {
                    $previous_misuse = $misuse;
                }
            }
            if ($reviewable_runs_with_current->count() == 1) {
                if (!$next_misuse) {
                    $next_misuse = $current_misuses->first();
                }
                if (!$previous_misuse) {
                    $previous_misuse = $current_misuses->last();
                }
            } else {
                $found = False;
                foreach ($runs as $key => $run) {
                    if ($found) {
                        $next_run = $run;
                        break;
                    }
                    if ($run->run_id == $current_run->id) {
                        $found = True;
                    }
                    if (!$found) {
                        $previous_run = $run;
                    }
                }
                $only_reviewable_runs = $reviewable_runs_with_current->filter(function ($value, $key) {
                    if ($value->misuses->isNotEmpty() && $value->misuses->contains(function ($value, $key) {
                            return $value->getReviewState() == ReviewState::NEEDS_REVIEW;
                        })) {
                        return True;
                    }
                    return False;
                });
                if (!$previous_run) {
                    $previous_run = $only_reviewable_runs->last();
                }
                if (!$next_run) {
                    $next_run = $only_reviewable_runs->first();
                }
                if (!$next_misuse) {
                    $next_misuse = $next_run->misuses->filter(function ($value, $key) {
                        return $value->getReviewState() == ReviewState::NEEDS_REVIEW;
                    })->first();
                }
                if (!$previous_misuse) {
                    $previous_misuse = $previous_run->misuses->filter(function ($value, $key) {
                        return $value->getReviewState() == ReviewState::NEEDS_REVIEW;
                    })->last();
                }
            }
        }
        $all_violation_types = Type::all();
        $all_tags = Tag::all();
        $review = $current_misuse->getReview($reviewer);
        return $this->renderer->render($response, 'review.phtml', ['reviewer' => $reviewer, 'is_reviewer' => $is_reviewer,
            'misuse' => $current_misuse, 'experiment' => $experiment,
            'detector' => $detector, 'review' => $review,
            'violation_types' => $all_violation_types, 'tags' => $all_tags, 'next_misuse' => $next_misuse, 'previous_misuse' => $previous_misuse]);
    }

    public function getTodo(Request $request, Response $response, array $args)
    {
        $experiment_id = $args['experiment_id'];
        $reviewer_name = $args['reviewer_name'];

        $experiment = Experiment::find($experiment_id);
        $reviewer = Reviewer::where(['name' => $reviewer_name])->first();

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
        $reviewer = Reviewer::where(['name' => $reviewer_name])->first();

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

        $reviewer_name = $args['reviewer_name'];
        $reviewer = Reviewer::where(['name' => $reviewer_name])->first();
        $this->updateOrCreateReview($misuse_id, $reviewer->id, $comment, $hits);

        if ($review["origin"] != "") {
            return $response->withRedirect("{$this->settings['site_base_url']}{$review["origin"]}");
        }else {
            return $response->withRedirect($this->router->pathFor("private.review", ["experiment_id" => $experiment_id,
                "detector_muid" => $detector_muid, "project_muid" => $project_muid, "version_muid" => $version_muid,
                "misuse_muid" => $misuse_muid, "reviewer_name" => $reviewer_name]));
        }
    }

    public function updateOrCreateReview($misuse_id, $reviewer_id, $comment, $findings_reviews_by_rank)
    {
        $review = Review::firstOrNew(['misuse_id' => $misuse_id, 'reviewer_id' => $reviewer_id]);
        $review->comment = $comment;
        $review->save();

        foreach ($findings_reviews_by_rank as $rank => $findings_review) {
            $findingReview = FindingReview::firstOrNew(['review_id' => $review->id, 'rank' => $rank]);
            $findingReview->decision = $findings_review['hit'];
            $findingReview->save();
            if($findings_review['types']){
                $findingReview->violation_types()->sync($findings_review['types']);
            }
        }
    }
}
