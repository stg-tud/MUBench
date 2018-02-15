<?php

namespace MuBench\ReviewSite\Controllers;


use Illuminate\Database\Eloquent\Collection;
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

        $all_misuses = $this->collectAllMisuses($runs);

        list($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse) =
            $this->determineNavigationTargets($all_misuses, $project_muid, $version_muid, $misuse_muid, $reviewer);

        $all_violation_types = Type::all();
        $all_tags = Tag::all();
        $review = $misuse->getReview($reviewer);
        return $this->renderer->render($response, 'review.phtml', ['reviewer' => $reviewer, 'is_reviewer' => $is_reviewer,
            'misuse' => $misuse, 'experiment' => $experiment,
            'detector' => $detector, 'review' => $review,
            'violation_types' => $all_violation_types, 'tags' => $all_tags, 'next_misuse' => $next_misuse, 'previous_misuse' => $previous_misuse, 'next_reviewable_misuse' => $next_reviewable_misuse]);
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
            $base_url = substr($this->settings['site_base_url'], -1) === '/' ? substr($this->settings['site_base_url'], 0, -1) : $this->settings['site_base_url'];
            return $response->withRedirect("{$base_url}{$review["origin"]}");
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
            $findingReview->violation_types()->sync($findings_review['types']);
        }
    }

    private function collectAllMisuses($runs)
    {
        $all_misuses = new Collection;
        foreach ($runs as $run) {
            $all_misuses = $all_misuses->merge($run->misuses);
        }
        return $all_misuses;
    }

    function determineNavigationTargets(Collection $all_misuses, $project_muid, $version_muid, $misuse_muid, $reviewer)
    {
        $previous_misuse = $all_misuses->last();
        $misuse = NULL;
        $next_misuse = NULL;
        $next_reviewable_misuse = NULL;

        foreach ($all_misuses as $current_misuse) { /** @var Misuse $current_misuse */
            if (!$misuse && $current_misuse->getProject() === $project_muid
                && $current_misuse->getVersion() === $version_muid
                && $current_misuse->misuse_muid === $misuse_muid) {
                $misuse = $current_misuse;
            } else {
                if ($misuse && !$next_misuse) {
                    $next_misuse = $current_misuse;
                }
                $is_current_misuse_reviewable = $current_misuse->getReviewState() === ReviewState::NEEDS_REVIEW
                    && !$current_misuse->hasReviewed($reviewer);
                $first_reviewable_misuse = !$next_reviewable_misuse && $is_current_misuse_reviewable;
                $first_reviewable_misuse_after = $misuse && $is_current_misuse_reviewable;
                if ($first_reviewable_misuse || $first_reviewable_misuse_after) {
                    $next_reviewable_misuse = $current_misuse;
                    if ($misuse) {
                        break;
                    }
                }
            }
            if (!$misuse) {
                $previous_misuse = $current_misuse;
            }
        }

        if (!$next_misuse) {
            $next_misuse = $all_misuses->first();
        }

        return array($previous_misuse, $next_misuse, $next_reviewable_misuse, $misuse);
    }

}
