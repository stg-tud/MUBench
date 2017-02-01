<?php

use Monolog\Logger;

class DBConnection
{

    private $pdo;
    private $logger;

    function __construct(PDO $pdo, Logger $logger)
    {
        $this->logger = $logger;
        $this->pdo = $pdo;
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
        $sql = $this->columnQuery($table);
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

    public function arrayToString($json)
    {
        $out = $json[0];
        for ($i = 1; $i < count($json); $i++) {
            $out = $out . ';' . $json[$i];
        }
        return $out;
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
}