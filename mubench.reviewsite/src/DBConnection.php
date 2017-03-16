<?php

namespace MuBench\ReviewSite;

use InvalidArgumentException;
use Monolog\Logger;
use MuBench\ReviewSite\Model\Detector;
use MuBench\ReviewSite\Model\Misuse;
use MuBench\ReviewSite\Model\Review;
use PDO;
use PDOException;

class DBConnection
{
    private $pdo;
    private $logger;

    function __construct(PDO $pdo, Logger $logger)
    {
        $this->logger = $logger;
        $this->pdo = $pdo;
    }

    public function quote($var){
        return $this->pdo->quote($var);
    }

    public function execStatements($statements)
    {
        foreach ($statements as $s) {
            $this->execStatement($s);
        }
    }

    public function execStatement($statement)
    {
        try {
            $status = $this->pdo->exec($statement);
            $this->logger->info("Status execStatement: " . $status . " executing . " . substr($statement, 0, 10));
        } catch (PDOException $e) {
            $this->logger->error("Error execStatement: (" . $e->getMessage() . ") executing " . $statement);
        }
    }

    public function getTableColumns($table)
    {
        if (empty($this->tryQuery("SHOW TABLES LIKE '$table'"))) {
            return []; // table does not exist
        } else {
            return array_keys(current($this->tryQuery("SELECT * FROM `$table` WHERE 1 LIMIT 1")));
        }
    }

    public function getTableName($detector)
    {
        $query = [];
        $sql = "SELECT `id` from `detectors` WHERE `name`=" . $this->pdo->quote($detector);
        try {
            $query = $this->pdo->query($sql);
        } catch (PDOException $e) {
            $this->logger->error("Error getTableName: " . $e->getMessage());
        }
        $columns = array();
        if (!$query) {
            return NULL;
        }
        foreach ($query as $q) {
            $columns[] = $q["id"];
        }
        if (empty($columns)) {
            $sql = "INSERT INTO `detectors` (`id`, `name`) VALUES (NULL, " . $this->pdo->quote($detector) . ")";
            try {
                $this->pdo->exec($sql);
            } catch (PDOException $e) {
                $this->logger->error("Error getTableName creating new entry: " . $e->getMessage());
            }
            return $this->getTableName($detector);
        } else {
            return "detector_" . $columns[0];
        }
    }

    public function getPatterns($misuse)
    {
        return $this->tryQuery("SELECT `name`, `code`, `line` FROM `patterns` WHERE `misuse`=" . $this->pdo->quote($misuse));
    }

    public function getReview($exp, $detector, $project, $version, $misuse, $name)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * FROM `reviews` WHERE `name`=" . $this->pdo->quote($name) .
                " AND `exp` = " . $this->pdo->quote($exp) .
                " AND `detector` = " . $this->pdo->quote($detector) .
                " AND `project` = " . $this->pdo->quote($project) .
                " AND `version` = " . $this->pdo->quote($version) .
                " AND `misuse` = " . $this->pdo->quote($misuse));
        } catch (PDOException $e) {
            $this->logger->error("Error getReview: " . $e->getMessage());
        }
        if (!$query) {
            return [];
        }
        foreach ($query as $q) {
            return $q;
        }
    }

    public function getReviewFinding($id, $rank)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * FROM `review_findings` WHERE `review`=" . $this->pdo->quote($id) .
                " AND `rank`=" . $this->pdo->quote($rank));
        } catch (PDOException $e) {
            $this->logger->error("Error getReviewFinding: " . $e->getMessage());
        }
        if (!$query) {
            return [];
        }
        foreach ($query as $q) {
            return $q;
        }
    }

    public function getReviewFindings($id)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * FROM `review_findings` WHERE `review`=" . $this->pdo->quote($id));
        } catch (PDOException $e) {
            $this->logger->error("Error getReviewFindings: " . $e->getMessage());
        }

        $review_findings = [];
        foreach($query as $t){
            $review_findings[] = $t;
        }
        return $review_findings;
    }

    public function getTypes()
    {
        return $this->tryQuery("SELECT * FROM `types`;");
    }

    public function getTypeIdByName($name)
    {
        $types = $this->tryQuery("SELECT * FROM `types` WHERE `name`=" . $this->pdo->quote($name));
        foreach ($types as $type) {
            if ($type['name'] === $name) {
                return $type['id'];
            }
        }
        return 0;
    }

    private function getDetectorTableName(Detector $detector)
    {
        return "detector_" . $detector->id;
    }

    private function tryQuery($query)
    {
        try {
            $statement = $this->pdo->query($query);
            $result = [];
            foreach ($statement as $row) {
                $result[] = $row;
            }
            return $result;
        } catch (PDOException $e) {
            $this->logger->error("Failed to '" . $query . "': " . $e->getMessage());
            return [];
        }
    }

    public function getRuns(Detector $detector, $experiment)
    {
        $detectorTableName = $this->getDetectorTableName($detector);

        $runs = $this->tryQuery("SELECT * FROM `stats` " .
            "WHERE `exp` = " . $this->pdo->quote($experiment) .
            "  AND `detector` LIKE " . $this->pdo->quote($detectorTableName) . " " .
            "ORDER BY `project`, `version`");

        foreach ($runs as &$run) {
            $project_id = $run["project"];
            $version_id = $run["version"];

            if (strcmp($experiment, "ex1") === 0) {
                $misuses = $this->tryQuery("SELECT * FROM `metadata`" .
                    "WHERE `metadata`.`project` = " . $this->pdo->quote($project_id) .
                    "  AND `metadata`.`version` = " . $this->pdo->quote($version_id) .
                    "  AND EXISTS (SELECT 1 FROM `patterns` WHERE `patterns`.`misuse` = `metadata`.`misuse`) " .
                    "   ORDER BY `metadata`.`misuse` * 1, `metadata`.`misuse`");
            } elseif (strcmp($experiment, "ex2") === 0) {
                $misuses = $this->tryQuery("SELECT `misuse` FROM `" . $detectorTableName . "`" .
                    "WHERE `" . $detectorTableName . "`.`exp` = " . $this->pdo->quote($experiment) .
                    "  AND `project` = " . $this->pdo->quote($project_id) .
                    "  AND `version` = " . $this->pdo->quote($version_id) . " " .
                    "ORDER BY `misuse` * 1, `misuse`");
            } elseif (strcmp($experiment, "ex3") === 0) {
                $misuses = $this->tryQuery("SELECT * FROM `metadata`" .
                    "WHERE `project` = " . $this->pdo->quote($project_id) .
                    "  AND `version` = " . $this->pdo->quote($version_id) . " " .
                    "ORDER BY `misuse` * 1, `misuse`");
            }

            foreach ($misuses as $key => $misuse) {
                $misuse_id = $misuse["misuse"];
                $potential_hits =
                    $this->getPotentialHits($experiment, $detector, $project_id, $version_id, $misuse_id);
                $reviews = $this->getReviews($experiment, $detector, $project_id, $version_id, $misuse_id);
                $snippet = $this->getSnippet($experiment, $detector, $project_id, $version_id, $misuse_id);
                $misuse["snippets"] = $snippet;
                if(strcmp($experiment, "ex1") == 0){
                    $patterns = $this->getPatterns($misuse_id);
                    $misuse["patterns"] = $patterns;
                }
                $misuses[$key] = new Misuse($misuse, $potential_hits, $reviews);
            }

            $run["misuses"] = $misuses;
        }

        return $runs;
    }

    public function getDetector($detector_name)
    {
        $result = $this->tryQuery("SELECT `id` FROM `detectors` WHERE `name` = " . $this->pdo->quote($detector_name));
        if (count($result) == 1) {
            return new Detector($detector_name, $result[0]["id"]);
        } else {
            throw new InvalidArgumentException("no such detector '" . $detector_name . "'");
        }
    }

    private function getReviews($experiment, Detector $detector, $project_id, $version_id, $misuse_id)
    {
        $reviews = $this->tryQuery("SELECT * FROM `reviews` " .
            "WHERE `exp` = " . $this->pdo->quote($experiment) .
            "  AND `detector` = " . $this->pdo->quote($detector->name) .
            "  AND `project` = " . $this->pdo->quote($project_id) .
            "  AND `version` = " . $this->pdo->quote($version_id) .
            "  AND `misuse`  = " . $this->pdo->quote($misuse_id));

        foreach ($reviews as $key => $review) {
            $review["finding_reviews"] = $this->getFindingReviews($review["id"]);
            $reviews[$key] = new Review($review);
        }

        return $reviews;
    }

    private function getSnippet($experiment, Detector $detector, $project_id, $version_id, $misuse_id)
    {
        $sql =
            "SELECT `line`, `snippet` FROM `meta_snippets` WHERE `project`=" . $this->pdo->quote($project_id) .
            " AND `version`=" .$this->pdo->quote($version_id) .
            " AND `misuse`=". $this->pdo->quote($misuse_id);
        if (strcmp($experiment, "ex2") == 0) {
            $sql = "SELECT `line`, `snippet` FROM `finding_snippets` WHERE `project`=". $this->pdo->quote($project_id) .
                " AND `version`=". $this->pdo->quote($version_id) .
                " AND `finding`=". $this->pdo->quote($misuse_id) .
                " AND `detector`=" . $this->pdo->quote($this->getDetectorTableName($detector));
        }
        $snippet = $this->tryQuery($sql);
        return $snippet;
    }

    private function getFindingReviews($review_id)
    {
        $finding_reviews = $this->tryQuery("SELECT * FROM `review_findings` " .
            "WHERE `review` = " . $this->pdo->quote($review_id));

        foreach ($finding_reviews as &$finding_review) {
            $violation_types = $this->tryQuery("SELECT `types`.`name` FROM `review_findings_type` " .
                "INNER JOIN `types` ON `review_findings_type`.`type` = `types`.`id` " .
                "WHERE `review_findings_type`.`review_finding` = " . $this->pdo->quote($finding_review["id"]));
            $finding_review["violation_types"] = [];
            foreach ($violation_types as $violation_type) {
                $finding_review["violation_types"][] = $violation_type["name"];
            }
        }
        return $finding_reviews;
    }

    public function getPotentialHits($experiment, Detector $detector, $project_id, $version_id, $misuse_id)
    {
        $potential_hits = $this->tryQuery("SELECT * FROM `" . $this->getDetectorTableName($detector) . "` " .
            "WHERE `exp` = " . $this->pdo->quote($experiment) .
            "  AND `project` = " . $this->pdo->quote($project_id) .
            "  AND `version` = " . $this->pdo->quote($version_id) .
            "  AND `misuse` = " . $this->pdo->quote($misuse_id));
        return $potential_hits;
    }

    public function getMisuse($experiment, $detector, $project, $version, $misuse){
        $runs = $this->getRuns($detector, $experiment);
        foreach($runs as $run){
            if(strcmp($run['project'], $project) == 0 && strcmp($run['version'], $version) == 0){
                foreach($run['misuses'] as $m){
                    if($m->id === $misuse){
                        return $m;
                        break;
                    }
                }
                break;
            }
        }
    }

    public function getDetectors($exp)
    {
        $detectors =
            $this->tryQuery("SELECT `name`, `id` FROM `detectors` WHERE EXISTS (" .
                "SELECT 1 FROM `stats` WHERE `exp`=" . $this->pdo->quote($exp) . " AND `detector` = CONCAT('detector_', `id`)" .
                ") ORDER BY `name`");
        $result = [];
        foreach ($detectors as $r) {
            $result[] = new Detector($r['name'], $r['id']);
        }
        return $result;
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

}