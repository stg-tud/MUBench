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

    function __construct($site_base_url, $upload_path, DBConnection $db, PhpRenderer $renderer)
    {
        $this->site_base_url = $site_base_url;
        $this->upload_path = $upload_path;
        $this->db = $db;
        $this->renderer = $renderer;
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

    private function getMisuse($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        $metadata = $this->getMetadata($experimentId, $detector, $projectId, $versionId, $misuseId);
        $potential_hits = $this->getPotentialHits($experimentId, $detector, $projectId, $versionId, $misuseId);
        // SMELL misuses don't need their review here
        return new Misuse($metadata, $potential_hits, []);
    }

    private function getMetadata($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        if ($experimentId === "ex1" || $experimentId === "ex3") {
            $metadata = $this->db->table('metadata')
                ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId)->first();

            $types = $this->db->table('misuse_types')->select('types.name')
                ->innerJoin('types', 'misuse_types.type', '=', 'types.id')->where('project', $projectId)
                ->where('version', $versionId)->where('misuse', $misuseId)->get();
            $metadata["violation_types"] = [];
            foreach($types as $type){
                $metadata["violation_types"][] = $type['name'];
            }

            if($experimentId === "ex1") {
                $metadata["patterns"] = $this->getPatterns($misuseId);
            }
        } else { // if ($experimentId === "ex2")
            $metadata = ["misuse" => $misuseId];
        }

        $metadata["snippets"] = $this->getSnippets($experimentId, $detector, $projectId, $versionId, $misuseId);
        $metadata["tags"] = $this->getTags($experimentId, $detector, $projectId, $versionId, $misuseId);

        return $metadata;
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

    private function getReview($experimentId, $detector, $projectId, $versionId, $misuseId, $reviewerName)
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

    private function getSnippets($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        $columns = ['line', 'snippet'];
        if (strcmp($experimentId, "ex2") == 0) {
            $columns[] = 'id'; // SMELL meta_findings do not have an id
            $query = $this->db->table('finding_snippets')->where('detector', $detector->id)
                ->where('project', $projectId)->where('version', $versionId)->where('finding', $misuseId);
        } else {
            $query = $this->db->table('meta_snippets')
                ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId);
        }
        return $query->select($columns)->get();
    }

    private function getTags($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        return $this->db->table('misuse_tags')->innerJoin('tags', 'misuse_tags.tag', '=', 'tags.id')
            ->select('id', 'name')->where('exp', $experimentId)->where('detector', $detector->id)
            ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId)->get();
    }

    private function getPatterns($misuse)
    {
        return $this->db->table('patterns')->select(['name', 'code', 'line'])->where('misuse', $misuse)->get();
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
}
