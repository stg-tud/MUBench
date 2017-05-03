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
        $this->query_builder->pdo()->exec("CREATE TABLE `$table_name` (" . implode(",", $columns) . ")");
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
        return $this->table('reviews')->where('name', $name)->where('exp', $exp)->where('detector', $detector->id)
            ->where('project', $project)->where('version', $version)->where('misuse', $misuse)->first();
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

    public function getRuns(Detector $detector, $exp)
    {
        /** @var array $runs */
        $runs = $this->table('stats')->where('exp', $exp)->where('detector', $detector->id)->orderBy(['project', 'version'])->get();

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
                $snippet = $this->getSnippet($exp, $detector, $project_id, $version_id, $misuse_id);
                $misuse["snippets"] = $snippet;
                if(strcmp($exp, "ex1") == 0){
                    $patterns = $this->getPatterns($misuse_id);
                    $misuse["patterns"] = $patterns;
                }
                $misuses[$key] = new Misuse($misuse, $potential_hits, $reviews);
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

    public function getDetectors($exp)
    {
        $detectors = [];
        foreach ($this->table('detectors')->orderBy('name')->get() as $detector) {
            if ($this->table('stats')->where('detector', $detector['id'])->where('exp', $exp)->first()) {
                $detectors[] = new Detector($detector['name'], $detector['id']);
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

    private function getSnippet($experiment, Detector $detector, $project_id, $version_id, $misuse_id)
    {
        if (strcmp($experiment, "ex2") == 0) {
            $query = $this->table('finding_snippets')->where('finding', $misuse_id)->where('detector', $detector->id);
        } else {
            $query = $this->table('meta_snippets')->where('misuse', $misuse_id);
        }
        return $query->select(['line', 'snippet'])->where('project', $project_id)->where('version', $version_id)->get();
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

    public function getTodo($reviewer){
        $experiment = ["ex1", "ex2", "ex3"];
        $misuses = [];
        foreach($experiment as $exp){
            $detectors = $this->getDetectors($exp);
            foreach($detectors as $detector){
                $runs = $this->getRuns($detector, $exp);
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

    private function getQualifiedName($table_name)
    {
        return $this->query_builder->addTablePrefix($table_name, false);
    }

}