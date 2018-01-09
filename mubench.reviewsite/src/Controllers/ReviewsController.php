<?php

namespace MuBench\ReviewSite\Controllers;


use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\FindingReview;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\Reviewer;
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
        $ex2_review_size = $request->getQueryParam("ex2_review_size", $this->default_ex2_review_size);

        $reviewer = array_key_exists('reviewer_name', $args) ? Reviewer::where(['name' => $args['reviewer_name']])->first() : $this->user;
        $resolution_reviewer = Reviewer::where(['name' => 'resolution'])->first();
        $is_reviewer = ($this->user && $reviewer && $this->user->id == $reviewer->id) || ($reviewer && $reviewer->id == $resolution_reviewer->id);

        $runs = RunsController::getRuns($detector, $experiment, $ex2_review_size);
        $current_run = Run::of($detector)->in($experiment)->where(['project_muid' => $project_muid, 'version_muid' => $version_muid])->first();

        $previous_run = $this->getRunWithMisuses($runs, $current_run->id, False);
        $next_run = $this->getRunWithMisuses($runs, $current_run->id, True);

        $misuse = $current_run->misuses()->where('misuse_muid', $misuse_muid)->first();

        $previous_misuse = $previous_run->misuses->last();
        $next_misuse = $next_run->misuses->first();
        $idx = 0;
        while($current_run->misuses[$idx]->misuse_muid !== $misuse_muid){
            $previous_misuse = $current_run->misuses[$idx];
            $idx = $idx + 1;
            if($current_run->misuses->count() === ($idx + 1)){
                $next_misuse = $next_run->misuses->first();
            }else{
                $next_misuse = $current_run->misuses[$idx + 1];
            }
        }
        if($idx == 0 && $current_run->misuses->count() > 1){
            $next_misuse = $current_run->misuses[$idx + 1];
        }

        $all_violation_types = Type::all();
        $all_tags = Tag::all();
        $review = $misuse->getReview($reviewer);
        return $this->renderer->render($response, 'review.phtml', ['reviewer' => $reviewer, 'is_reviewer' => $is_reviewer,
            'misuse' => $misuse, 'experiment' => $experiment,
            'detector' => $detector, 'review' => $review,
            'violation_types' => $all_violation_types, 'tags' => $all_tags, 'next_misuse' => $next_misuse, 'previous_misuse' => $previous_misuse]);
    }

    private function getRunWithMisuses($runs, $run_id, $forward)
    {
        foreach($runs as $key => $run){
            if($run->id === $run_id){
                $run_idx = $key;
                break;
            }
        }
        $idx = $run_idx + ($forward ?  1 : -1);
        if($idx === -1){
            $idx = $runs->count() - 1;
        }else if($idx === $runs->count()){
            $idx = 0;
        }
        $run = $runs[$idx];
        while($run->misuses->isEmpty() && $idx !== ($forward ? $runs->count() : -1)){
            $run = $runs[$idx];
            $idx = $forward ? ($idx + 1) : ($idx - 1);
        }
        if($run->misuses->isEmpty()){
            $run = $runs[$run_idx];
        }
        return $run;
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
