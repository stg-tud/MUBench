<?php

use Monolog\Logger;
use MuBench\Detector;
use MuBench\Misuse;

class DBConnection
{

    private $pdo;
    private $logger;
    private $queryBuilder;

    function __construct(PDO $pdo, Logger $logger)
    {
        $this->logger = $logger;
        $this->pdo = $pdo;
        $this->queryBuilder = new QueryBuilder($pdo, $logger);
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
        $sql = $this->queryBuilder->columnQuery($table);
        $query = [];
        try {
            $query = $this->pdo->query($sql);
        } catch (PDOException $e) {
            $this->logger->error("Error getTableColumns: " . $e->getMessage());
        }
        $columns = array();
        if (!$query) {
            return $columns;
        }
        foreach ($query as $q) {
            $columns[] = $q[0];
        }
        return $columns;
    }

    public function getTableName($detector)
    {
        $query = [];
        $sql = "SELECT id from detectors WHERE name=" . $this->pdo->quote($detector) . ";";
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
            $columns[] = $q[0];
        }
        if (empty($columns)) {
            $sql = "INSERT INTO detectors (name) VALUES(" . $this->pdo->quote($detector) . ");";
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

    public function getAllReviews()
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from reviews;");
        } catch (PDOException $e) {
            $this->logger->error("Error getAllReview: " . $e->getMessage());
        }
        return $query;
    }

    public function getDetectorTable($detector)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT id FROM detectors WHERE name=" . $this->pdo->quote($detector) . ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getDetectorTable: " . $e->getMessage());
        }
        foreach ($query as $q) {
            return "detector_" . $q[0];
        }

    }

    public function hasFindingForExp($exp, $detector)
    {
        $query = [];
        try {
            $query =
                $this->pdo->query("SELECT * FROM " . $detector . " WHERE exp=" . $this->pdo->quote($exp) . " LIMIT 1;");
        } catch (PDOException $e) {
            $this->logger->error("Error findingForExp: " . $e->getMessage());
        }
        $tables = [];
        foreach ($query as $q) {
            $tables[] = $q[0];
        }
        return !empty($tables);
    }

    public function getDetectorsTables()
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * FROM  detectors;");
        } catch (PDOException $e) {
            $this->logger->error("Error getTables: " . $e->getMessage());
        }
        $tables = array();
        if (count($query) == 0) {
            return $tables;
        }
        foreach ($query as $q) {
            $detector = [];
            $detector['name'] = $q['name'];
            $detector['id'] = "detector_" . $q['id'];
            $tables[] = $detector;
        }
        return $tables;
    }

    public function hasStats($exp, $detector_table)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * FROM stats WHERE detector=" .
                $this->pdo->quote($detector_table) .
                " AND exp=" .
                $this->pdo->quote($exp) .
                ";");
        } catch (PDOException $e) {
            $this->logger->error("Error hasStats: " . $e->getMessage());
        }
        $result = $this->queryToArray($query);
        return count($result) > 0;
    }

    public function getAllStats($exp, $detector)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * FROM stats WHERE detector=" .
                $this->pdo->quote($detector) .
                " AND exp=" .
                $this->pdo->quote($exp) .
                ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getAllStats: " . $e->getMessage());
        }
        return $this->queryToArray($query);
    }

    public function getSmallDataPotentialHits($table, $exp)
    {
        $statement = "SELECT project, version, misuse FROM " . $table . ";";
        if ($exp === "ex2") {
            $statement = "SELECT project, version, id FROM " . $table . ";";
        }
        $query = [];
        try {
            $query = $this->pdo->query($statement);
        } catch (PDOException $e) {
            $this->logger->error("Error getSmallDataPotentialHits: " . $e->getMessage());
        }
        return $query;
    }

    public function getMetadata($project, $version, $misuse)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from metadata WHERE project=" .
                $this->pdo->quote($project) .
                " AND version=" .
                $this->pdo->quote($version) .
                " AND misuse=" .
                $this->pdo->quote($misuse) .
                ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getMetadata: " . $e->getMessage());
        }
        return $query;
    }

    public function getMetaSnippets($project, $version, $misuse)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT snippet, line from meta_snippets WHERE project=" .
                $this->pdo->quote($project) .
                " AND version=" .
                $this->pdo->quote($version) .
                " AND misuse=" .
                $this->pdo->quote($misuse) .
                ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getMetaSnippets: " . $e->getMessage());
        }
        return $query;
    }

    public function getPattern($misuse)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from patterns WHERE misuse=" . $this->pdo->quote($misuse) . ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getPattern: " . $e->getMessage());
        }
        return $query;
    }

    public function getReview($exp, $detector, $project, $version, $misuse, $name)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from reviews WHERE name=" .
                $this->pdo->quote($name) .
                " AND exp=" .
                $this->pdo->quote($exp) .
                " AND detector=" .
                $this->pdo->quote($detector) .
                " AND project=" .
                $this->pdo->quote($project) .
                " AND version=" .
                $this->pdo->quote($version) .
                " AND misuse=" .
                $this->pdo->quote($misuse) .
                ";");
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

    public function getHits($table, $project, $version, $misuse, $exp)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from " .
                $table .
                " WHERE exp=" .
                $this->pdo->quote($exp) .
                " AND misuse=" .
                $this->pdo->quote($misuse) .
                " AND project=" .
                $this->pdo->quote($project) .
                " AND version=" .
                $this->pdo->quote($version) .
                " ORDER BY `rank` * 1 ASC;");
        } catch (PDOException $e) {
            $this->logger->error("Error getHits: " . $e->getMessage());
        }
        return $query;
    }

    public function getMisusesFromMeta($project, $version)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * FROM metadata WHERE project=" .
                $this->pdo->quote($project) .
                " AND version=" .
                $this->pdo->quote($version) .
                ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getMisusesFromMeta: " . $e->getMessage());
        }
        return $query;
    }

    public function getPotentialHits($table, $exp, $project, $version)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from " .
                $table .
                " WHERE exp=" .
                $this->pdo->quote($exp) .
                " AND project=" .
                $this->pdo->quote($project) .
                " AND version=" .
                $this->pdo->quote($version) .
                ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getPotentialHits: " . $e->getMessage());
        }
        return $this->queryToArray($query);
    }

    public function getReviewsByIdentifier($exp, $detector, $project, $version, $misuse)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT name,id from reviews WHERE exp=" .
                $this->pdo->quote($exp) .
                " AND detector=" .
                $this->pdo->quote($detector) .
                " AND project=" .
                $this->pdo->quote($project) .
                " AND version=" .
                $this->pdo->quote($version) .
                " AND misuse=" .
                $this->pdo->quote($misuse) .
                " ORDER BY `name`;");
        } catch (PDOException $e) {
            $this->logger->error("Error getReviewsByIdentifier: " . $e->getMessage());
        }
        return $query;
    }

    public function getReviewsByReviewer($reviewer)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from reviews WHERE name=" .
                $this->pdo->quote($reviewer) .
                " ORDER BY `exp`, `detector`, `project`, `version`, `misuse`;");
        } catch (PDOException $e) {
            $this->logger->error("Error getReviewsByReviewer: " . $e->getMessage());
        }
        return $query;
    }


    public function getReviewFinding($id, $rank)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from review_findings WHERE review=" .
                $this->pdo->quote($id) .
                "AND rank=" .
                $this->pdo->quote($rank) .
                ";");
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
            $query = $this->pdo->query("SELECT * from review_findings WHERE review=" . $this->pdo->quote($id) . ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getReviewFindings: " . $e->getMessage());
        }
        return $this->queryToArray($query);
    }

    public function getTypes()
    {
        return $this->execQuery("SELECT * from types;");
    }

    public function execQuery($sql)
    {
        $query = [];
        try {
            $query = $this->pdo->query($sql);
        } catch (PDOException $e) {
            $this->logger->error("Error getTypes: " . $e->getMessage());
        }
        return $this->queryToArray($query);
    }

    public function queryToArray($query)
    {
        if (!$query) {
            return [];
        }
        $result = [];
        foreach ($query as $q) {
            $result[] = $q;
        }
        return $result;
    }

    public function getTypeIdByName($name)
    {
        $types = $this->execQuery("SELECT * from types WHERE name=" . $this->pdo->quote($name) . ";");
        foreach ($types as $type) {
            if ($type['name'] === $name) {
                return $type['id'];
            }
        }
        return 0;
    }

    public function getTypeNameById($id)
    {
        $types = $this->execQuery("SELECT * from types WHERE id=" . $this->pdo->quote($id) . ";");
        foreach ($types as $type) {
            if ($type['id'] === $id) {
                return $type['name'];
            }
        }
        return "unknown";
    }

    public function getReviewTypes($id)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT * from review_findings_type WHERE review_finding=" .
                $this->pdo->quote($id) .
                ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getTypes: " . $e->getMessage());
        }
        if (!$query) {
            return [];
        }
        $result = [];
        foreach ($query as $q) {
            $result[] = $this->getTypeNameById($q['type']);
        }
        return $result;
    }

    public function getFindingSnippet($detector, $project, $version, $finding)
    {
        $query = [];
        try {
            $query = $this->pdo->query("SELECT snippet, line from finding_snippets WHERE detector=" .
                $this->pdo->quote($detector) .
                " AND project=" .
                $this->pdo->quote($project) .
                " AND version=" .
                $this->pdo->quote($version) .
                " AND finding=" .
                $this->pdo->quote($finding) .
                ";");
        } catch (PDOException $e) {
            $this->logger->error("Error getFindingSnippet: " . $e->getMessage());
        }
        return $this->queryToArray($query);
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
                $misuses = $this->tryQuery("SELECT * FROM `metadata` " .
                    "WHERE `project` = " . $this->pdo->quote($project_id) .
                    "  AND `version` = " . $this->pdo->quote($version_id) .
                    "  AND EXISTS (SELECT 1 FROM `patterns` WHERE `patterns`.`misuse` = `metadata`.`misuse`) " .
                    "ORDER BY `misuse` * 1, `misuse`");
            } elseif (strcmp($experiment, "ex2") === 0) {
                $misuses = $this->tryQuery("SELECT `misuse` FROM `" . $detectorTableName . "` " .
                    "WHERE `exp` = " . $this->pdo->quote($experiment) .
                    "  AND `project` = " . $this->pdo->quote($project_id) .
                    "  AND `version` = " . $this->pdo->quote($version_id) . " " .
                    "ORDER BY `misuse` * 1, `misuse`");
            } elseif (strcmp($experiment, "ex3") === 0) {
                $misuses = $this->tryQuery("SELECT * FROM `metadata` " .
                    "WHERE `project` = " . $this->pdo->quote($project_id) .
                    "  AND `version` = " . $this->pdo->quote($version_id) . " " .
                    "ORDER BY `misuse` * 1, `misuse`");
            }

            foreach ($misuses as $key => $misuse) {
                $misuse_id = $misuse["misuse"];
                $potential_hits = $this->getPotentialHits2($experiment, $detector, $project_id, $version_id, $misuse_id);
                $reviews = $this->getReviews($experiment, $detector, $project_id, $version_id, $misuse_id);

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

        foreach ($reviews as &$review) {
            $review["finding_reviews"] = $this->getFindingReviews($review["id"]);
        }

        return $reviews;
    }

    private function getFindingReviews($review_id)
    {
        $finding_reviews = $this->tryQuery("SELECT * FROM `review_findings` " .
            "WHERE `review` = " . $this->pdo->quote($review_id));

        foreach ($finding_reviews as &$finding_review) {
            $violation_types = $this->tryQuery("SELECT `types`.`name` FROM `review_finding_types` " .
                "INNER JOIN `types` ON `review_finding_types`.`type` = `types`.`id` " .
                "WHERE `review_finding_types`.`review_finding` = " . $this->pdo->quote($finding_review["id"]));

            $finding_review["violation_types"] = [];
            foreach ($violation_types as $violation_type) {
                $finding_review["violation_types"][] = $violation_type["name"];
            }
        }
        return $finding_reviews;
    }

    public function getPotentialHits2($experiment, Detector $detector, $project_id, $version_id, $misuse_id)
    {
        $potential_hits = $this->tryQuery("SELECT * FROM `" . $this->getDetectorTableName($detector) . "` " .
            "WHERE `exp` = " . $this->pdo->quote($experiment) .
            "  AND `project` = " . $this->pdo->quote($project_id) .
            "  AND `version` = " . $this->pdo->quote($version_id) .
            "  AND `misuse`  = " . $this->pdo->quote($misuse_id));
        return $potential_hits;
    }
}