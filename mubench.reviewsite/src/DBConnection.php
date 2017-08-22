<?php

namespace MuBench\ReviewSite;

use Monolog\Logger;
use MuBench\ReviewSite\Model\Detector;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\Review;
use PDO;
use Pixie\Connection;
use Pixie\QueryBuilder\QueryBuilderHandler;

class DBConnection
{
    /** @var QueryBuilderHandler */
    private $query_builder;

    /** @var Logger */
    private $logger;

    function __construct(Connection $connection, Logger $logger)
    {
        $this->query_builder = $connection->getQueryBuilder();
        $this->logger = $logger;
    }

    /**
     * @param string $table_name
     * @return QueryBuilderHandler
     */
    public function table($table_name)
    {
        /** @noinspection PhpParamsInspection */
        return $this->query_builder->table($table_name)->setFetchMode(PDO::FETCH_ASSOC);
    }

    public function create_table($table_name, array $columns)
    {
        $table_name = $this->getQualifiedName($table_name);
        $this->query_builder->pdo()->exec("CREATE TABLE IF NOT EXISTS `$table_name` (" . implode(",", $columns) . ")");
    }

    public function add_column($table_name, $column)
    {
        $table_name = $this->getQualifiedName($table_name);
        $this->query_builder->pdo()->exec("ALTER TABLE `$table_name` ADD $column");
    }

    public function last_insert_id()
    {
        return $this->query_builder->pdo()->lastInsertId();
    }

    public function getPatterns($misuse)
    {
        return $this->table('patterns')->select(['name', 'code', 'line'])->where('misuse', $misuse)->get();
    }

    public function getReview($exp, Detector $detector, $project, $version, $misuse, $name)
    {
        return $this->table('reviews')->where('exp', $exp)->where('detector', $detector->id)
            ->where('project', $project)->where('version', $version)->where('misuse', $misuse)->where('name', $name)->first();
    }

    public function getReviewFinding($id, $rank)
    {
        return $this->table('review_findings')->where('review', $id)->where('rank', $rank)->first();
    }

    public function getReviewFindings($id)
    {
        return $this->table('review_findings')->where('review', $id)->get();
    }

    public function getTypeIdByName($name)
    {
        return $this->table('types')->where('name', $name)->first()['id'];
    }

    public function getAllViolationTypes()
    {
        return $this->table('types')->get();
    }

    public function getRuns(Detector $detector, $exp, $max_reviews = -1)
    {
        /** @var array $runs */
        $runs = $this->table($detector->getStatsTableName())->where('exp', $exp)->orderBy(['project', 'version'])->get();

        foreach ($runs as &$run) {
            $project_id = $run["project"];
            $version_id = $run["version"];

            $misuse_column = 'misuse';
            if (strcmp($exp, "ex1") === 0) {
                $misuse_column = $this->getQualifiedName('metadata.misuse');
                $query = $this->table('metadata')->select('metadata.*')
                    ->innerJoin('patterns', 'metadata.misuse', '=', 'patterns.misuse');
            } elseif (strcmp($exp, "ex2") === 0) {
                $query = $this->table($detector->getTableName())->select('misuse')->where('exp', $exp);
            } else { // if (strcmp($exp, "ex3") === 0)
                $query = $this->table('metadata');
            }
            $misuses = $query->where('project', $project_id)->where('version', $version_id)
                ->orderBy($this->query_builder->raw("$misuse_column * 1,"), $misuse_column)->get();

            foreach ($misuses as $key => $misuse) {
                $misuse_id = $misuse["misuse"];
                /** @var array $potential_hits */
                $potential_hits = $this->getPotentialHits($exp, $detector, $project_id, $version_id, $misuse_id);
                /** @var array $reviews */
                $reviews = $this->getReviews($exp, $detector, $project_id, $version_id, $misuse_id);
                $snippets = $this->getSnippets($exp, $detector, $project_id, $version_id, $misuse_id);
                if(strcmp($exp, "ex2") !== 0){
                    $misuse["violation_types"] = $this->getViolationTypeNamesForMisuse($project_id, $version_id, $misuse_id);
                }
                $misuse["snippets"] = $snippets;
                $misuse["tags"] = $this->getTagsForMisuse($exp, $detector->id, $project_id, $version_id, $misuse_id);

                if(strcmp($exp, "ex1") == 0){
                    $patterns = $this->getPatterns($misuse_id);
                    $misuse["patterns"] = $patterns;
                }
                $misuses[$key] = new Misuse($misuse, $potential_hits, $reviews);
            }
            if($max_reviews > -1 && strcmp($exp, "ex2") == 0){
                $misuses = $this->filterMisusesForMaxReviews($misuses, $max_reviews);
            }
            $run["misuses"] = $misuses;
        }
        return $runs;
    }

    public function getOrCreateDetector($detector_name)
    {
        $detector_data = $this->table('detectors')->select('id')->where('name', $detector_name)->first();
        if ($detector_data) {
            $detector_id = $detector_data['id'];
        } else {
            $detector_id = $this->table('detectors')->insert(['name' => $detector_name]);
        }
        return new Detector($detector_name, $detector_id);
    }

    public function getDetector($detector_name)
    {
        $detector_data = $this->table('detectors')->select('id')->where('name', $detector_name)->first();
        if($detector_data){
            return new Detector($detector_name, $detector_data['id']);
        }
        throw new \InvalidArgumentException("no detector with name $detector_name");
    }

    public function getDetectors($exp)
    {
        $detectors = [];
        foreach ($this->table('detectors')->orderBy('name')->get() as $dt) {
            $detector = new Detector($dt['name'], $dt['id']);
            if ($this->table($detector->getStatsTableName())->where('exp', $exp)->first()) {
                $detectors[] = $detector;
            }
        }
        return $detectors;
    }

    private function getReviews($experiment, Detector $detector, $project_id, $version_id, $misuse_id)
    {
        $reviews = $this->table('reviews')
            ->where('exp', $experiment)->where('detector', $detector->id)->where('project', $project_id)
            ->where('version', $version_id)->where('misuse', $misuse_id)->get();

        foreach ($reviews as $key => $review) {
            $review["finding_reviews"] = $this->getFindingReviews($review["id"]);
            $reviews[$key] = new Review($review);
        }

        return $reviews;
    }

    private function getSnippets($experiment, Detector $detector, $project_id, $version_id, $misuse_id)
    {
        $columns = ['line', 'snippet'];
        if (strcmp($experiment, "ex2") == 0) {
            $columns[] = 'id';
            $query = $this->table('finding_snippets')->where('detector', $detector->id)
                ->where('project', $project_id)->where('version', $version_id)->where('finding', $misuse_id);
        } else {
            $query = $this->table('meta_snippets')
                ->where('project', $project_id)->where('version', $version_id)->where('misuse', $misuse_id);
        }
        return $query->select($columns)->get();
    }

    private function getFindingReviews($review_id)
    {
        $finding_reviews = $this->table('review_findings')->where('review', $review_id)->get();

        foreach ($finding_reviews as &$finding_review) {
            $violation_types = $this->table('review_findings_types')
                ->innerJoin('types', 'review_findings_types.type', '=', 'types.id')->select('name')
                ->where('review_finding', $finding_review['id'])->get();
            $finding_review["violation_types"] = [];
            foreach ($violation_types as $violation_type) {
                $finding_review["violation_types"][] = $violation_type["name"];
            }
        }
        return $finding_reviews;
    }

    public function getPotentialHits($experiment, Detector $detector, $project_id, $version_id, $misuse_id)
    {
        return $this->table($detector->getTableName())
            ->where('exp', $experiment)->where('project', $project_id)
            ->where('version', $version_id)->where('misuse', $misuse_id)
            ->orderBy($this->query_builder->raw("`rank` * 1"))->get();
    }

    private function getViolationTypeNamesForMisuse($project, $version, $misuse)
    {
        $types = $this->table('misuse_types')->select('types.name')->innerJoin('types', 'misuse_types.type', '=', 'types.id')->where('project', $project)->where('version', $version)->where('misuse', $misuse)->get();
        $type_names = array();
        foreach($types as $type){
            $type_names[] = $type['name'];
        }
        return $type_names;
    }

    private function getViolationTypeForId($type_id)
    {
        return $this->table('types')->select('name')->where('id', $type_id)->first();
    }

    public function getMisuse($experiment, $detector, $project, $version, $misuse){
        $runs = $this->getRuns($detector, $experiment);
        foreach($runs as $run){
            if(strcmp($run['project'], $project) == 0 && strcmp($run['version'], $version) == 0){
                foreach($run['misuses'] as $m){
                    /** @var Misuse $m */
                    if($m->id === $misuse){
                        return $m;
                    }
                }
                break;
            }
        }
        throw new \InvalidArgumentException("no such misuse $experiment, $detector, $project, $version, $misuse");
    }

    public function getAllReviews($reviewer){
        $experiment = ["ex1", "ex2", "ex3"];
        $misuses = [];
        foreach($experiment as $exp){
            $detectors = $this->getDetectors($exp);
            foreach($detectors as $detector){
                $runs = $this->getRuns($detector, $exp);
                foreach($runs as $run){
                    foreach($run['misuses'] as $misuse){
                        /** @var Misuse $misuse */
                        if($misuse->hasReviewed($reviewer)){
                            $misuses[$exp][$detector->name][] = $misuse;
                        }
                    }
                }
            }

        }
        return $misuses;
    }

    public function getTodo($reviewer, $max_reviews){
        $experiment = ["ex1", "ex2", "ex3"];
        $misuses = [];
        foreach($experiment as $exp){
            $detectors = $this->getDetectors($exp);
            foreach($detectors as $detector){
                $runs = $this->getRuns($detector, $exp, $max_reviews);
                foreach($runs as $run){
                    foreach($run['misuses'] as $misuse){
                        /** @var Misuse $misuse */
                        if(!$misuse->hasReviewed($reviewer) && !$misuse->hasSufficientReviews() && $misuse->hasPotentialHits()){
                            $misuses[$exp][$detector->name][] = $misuse;
                        }
                    }
                }
            }

        }
        return $misuses;
    }

    public function getTaggedMisuses($experiment, $detector, $tag)
    {
        return $this->table('misuse_tags')->where('exp', $experiment)->where('detector', $detector->id)->where('tag', $tag)->get();
    }

    public function getAllTags()
    {
        return $this->table('tags')->get();
    }

    public function getTagsForMisuse($experiment, $detector, $project, $version, $misuse)
    {
        return $this->table('misuse_tags')->innerJoin('tags', 'misuse_tags.tag', '=', 'tags.id')->select('id', 'name')->where('exp', $experiment)->where('detector', $detector)
            ->where('project', $project)->where('version', $version)->where('misuse', $misuse)->get();
    }

    public function getMisuseCountForType($type_id)
    {
        return $this->table('misuse_types')->select('type')->where('type', $type_id)->count();
    }

    private function getQualifiedName($table_name)
    {
        return $this->query_builder->addTablePrefix($table_name, false);
    }


    private function filterMisusesForMaxReviews($misuses, $max_reviews)
    {
            $conclusive_reviews = 0;
            $filtered_misuses = [];
            foreach ($misuses as $misuse) {
                if ($conclusive_reviews >= $max_reviews) {
                    break;
                }
                $filtered_misuses[] = $misuse;
                if ($misuse->hasConclusiveReviewState() || (!$misuse->hasSufficientReviews() && !$misuse->hasInconclusiveReview())) {
                    $conclusive_reviews++;
                }
            }
            return $filtered_misuses;
    }

}