<?php

namespace MuBench\ReviewSite\Controller;


use MuBench\ReviewSite\DBConnection;
use MuBench\ReviewSite\Model\Detector;
use MuBench\ReviewSite\Model\Experiment;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\Review;
use Slim\Http\Request;
use Slim\Http\Response;
use Slim\Views\PhpRenderer;

class ReviewController
{
    /** @var string */
    private $site_base_url;
    /** @var string */
    private $upload_path;
    /** @var DBConnection */
    private $db;
    /** @var PhpRenderer */
    private $renderer;
    /** @var MetadataController */
    private $metadataController;

    function __construct($site_base_url, $upload_path, DBConnection $db, PhpRenderer $renderer, MetadataController $metadataController)
    {
        $this->site_base_url = $site_base_url;
        $this->upload_path = $upload_path;
        $this->db = $db;
        $this->renderer = $renderer;
        $this->metadataController = $metadataController;
    }

    public function get(Request $request, Response $response, array $args)
    {
        $experimentId = $args['exp'];
        $detector = $this->getDetector($args['detector'], $request, $response);
        $projectId = $args['project'];
        $versionId = $args['version'];
        $misuseId = $args['misuse'];

        $user = $this->getUser($request);
        $reviewerName = array_key_exists('reviewer', $args) ? $args['reviewer'] : $user;
        $is_reviewer = strcmp($user, $reviewerName) == 0 || strcmp($reviewerName, "resolution") == 0;

        $misuse = $this->getMisuse($experimentId, $detector, $projectId, $versionId, $misuseId);
        $review = $this->getReview($experimentId, $detector, $projectId, $versionId, $misuseId, $reviewerName);

        // SMELL do we need these getter on the db?
        $all_violation_types = $this->db->getAllViolationTypes();
        // SMELL do we need these getter on the db?
        $all_tags = $this->db->getAllTags();

        return $this->render($request, $response, $args, 'review.phtml',
            ['reviewer' => $reviewerName, 'is_reviewer' => $is_reviewer,
                'misuse' => $misuse, 'review' => $review,
                'violation_types' => $all_violation_types, 'tags' => $all_tags]);
    }

    function getMisuse($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        $metadata = $this->metadataController->getMetadata($experimentId, $detector, $projectId, $versionId, $misuseId);
        $potential_hits = $this->getPotentialHits($experimentId, $detector, $projectId, $versionId, $misuseId);
        // SMELL misuses don't need their review here
        return new Misuse($metadata, $potential_hits, []);
    }

    /**
     * @return null|array
     */
    private function getPotentialHits($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        /** @noinspection PhpIncompatibleReturnTypeInspection */
        return $this->db->table($detector->getTableName())
            ->where('exp', $experimentId)->where('project', $projectId)
            ->where('version', $versionId)->where('misuse', $misuseId)
            ->orderBy($this->db->raw("`rank` * 1"))->get();
    }

    function getReview($experimentId, $detector, $projectId, $versionId, $misuseId, $reviewerName)
    {
        /** @var array $review */
        $review = $this->db->table('reviews')->where('exp', $experimentId)->where('detector', $detector->id)
            ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId)
            ->where('name', $reviewerName)->first();
        $review["finding_reviews"] = $this->getFindingReviews($review["id"]);
        return new Review($review);
    }

    private function getFindingReviews($reviewId)
    {
        /** @var array $finding_reviews */
        $finding_reviews = $this->db->table('review_findings')->where('review', $reviewId)
            ->orderBy($this->db->raw("`rank` * 1"))->get();

        foreach ($finding_reviews as &$finding_review) {
            $violation_types = $this->db->table('review_findings_types')
                ->innerJoin('types', 'review_findings_types.type', '=', 'types.id')->select('name')
                ->where('review_finding', $finding_review['id'])->get();
            // REFACTOR return ['id', 'name'] and adjust template
            $finding_review["violation_types"] = [];
            foreach ($violation_types as $violation_type) {
                $finding_review["violation_types"][] = $violation_type["name"];
            }
        }
        return $finding_reviews;
    }

    private function render(Request $request, Response $response, array $args, $template, array $params)
    {
        $params["user"] = $this->getUser($request);

        $params["site_base_url"] = htmlspecialchars($this->site_base_url);
        $params["public_url_prefix"] = $params["site_base_url"] . "index.php/";
        $params["private_url_prefix"] = $params["site_base_url"] . "index.php/private/";
        $params["api_url_prefix"] = $params["site_base_url"] . "index.php/api/";
        $params["uploads_url_prefix"] = $params["site_base_url"] . $this->upload_path;
        $params["url_prefix"] = $params["user"] ? $params["private_url_prefix"] : $params["public_url_prefix"];

        $path = $request->getUri()->getPath();
        $params["path"] = htmlspecialchars(strcmp($path, "/") === 0 ? "" : $path);
        $params["origin_param"] = htmlspecialchars("?origin=" . $params["path"]);
        $params["origin_path"] = htmlspecialchars($request->getQueryParam("origin", ""));

        $params["experiment"] = Experiment::get($args["exp"]);
        $params["experiments"] = Experiment::all();
        $params["detector"] = $this->getDetector($args['detector'], $request, $response);
        $params["detectors"] = [];
        foreach ($params["experiments"] as $experiment) { /** @var Experiment $experiment */
            $params["detectors"][$experiment->getId()] = $this->db->getDetectors($experiment->getId());
        }

        return $this->renderer->render($response, $template, $params);
    }

    private function getDetector($detector_name, $request, $response)
    {
        try{
            return $this->db->getDetector($detector_name);
        }catch (\InvalidArgumentException $e){
            throw new \Slim\Exception\NotFoundException($request, $response);
        }
    }

    private function getUser(Request $request)
    {
        $params = $request->getServerParams();
        return array_key_exists('PHP_AUTH_USER', $params) ? $params['PHP_AUTH_USER'] : "";
    }

    public function update(Request $request, Response $response, array $args)
    {
        $review = $request->getParsedBody();

        // REFACTOR remove 'review_exp' and 'review_detector' from template and use $args here.
        $experimentId = $review['review_exp'];
        $detector = $this->getDetector($review['review_detector'], $request, $response);
        $projectId = $review['review_project'];
        $versionId = $review['review_version'];
        $misuseId = $review['review_misuse'];
        $reviewerName = $review['review_name'];
        $comment = $review['review_comment'];
        $hits = $review['review_hit'];

        $this->updateReview($experimentId, $detector, $projectId, $versionId, $misuseId, $reviewerName, $comment, $hits);

        if (strcmp($review["origin"], "") !== 0) {
            return $response->withRedirect("{$this->site_base_url}index.php/{$review["origin"]}");
        } else {
            return $response->withRedirect("{$this->site_base_url}index.php/private/{$args['exp']}/{$args['detector']}");
        }
    }

    function updateReview($experimentId, $detector, $projectId, $versionId, $misuseId, $reviewerName, $comment, $hits)
    {
        $this->deleteReview($experimentId, $detector, $projectId, $versionId, $misuseId, $reviewerName);
        $this->saveReview($experimentId, $detector, $projectId, $versionId, $misuseId, $reviewerName, $comment, $hits);
    }

    private function deleteReview($experimentId, Detector $detector, $projectId, $versionId, $misuseId, $reviewerName)
    {
        $review = $review = $this->db->table('reviews')->where('exp', $experimentId)->where('detector', $detector->id)
            ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId)
            ->where('name', $reviewerName)->first();
        if ($review) {
            $reviewId = intval($review["id"]);
            $this->db->table('reviews')->where('id', $reviewId)->delete();
            foreach ($this->getFindingReviews($reviewId) as $findingReview) {
                $findingId = intval($findingReview['id']);
                $this->db->table('review_findings')->where('id', $findingId)->delete();
                $this->db->table('review_findings_types')->where('review_finding', $findingId)->delete();
            }
        }
    }

    private function saveReview($experimentId, Detector $detector, $projectId, $versionId, $misuseId, $reviewerName, $comment, $findingReviews)
    {
        $reviewId = $this->db->table('reviews')->insert(['exp' => $experimentId,'detector' => $detector->id,
            'project' => $projectId, 'version' => $versionId, 'misuse' => $misuseId, 'name' => $reviewerName,
            'comment' => $comment]);
        foreach ($findingReviews as $rank => $findingReview) {
            $findingId = $this->db->table('review_findings')
                ->insert(['review' => $reviewId, 'rank' => $rank, 'decision' => $findingReview['hit']]);
            if (array_key_exists("types", $findingReview)) {
                foreach ($findingReview['types'] as $type) {
                    $this->db->table('review_findings_types')->insert(['review_finding' => $findingId, 'type' => $type]);
                }
            }
        }
    }
}
