<?php

use Monolog\Logger;

class QueryBuilder
{
    private $pdo;
    private $logger;

    function __construct(PDO $pdo, Logger $logger)
    {
        $this->logger = $logger;
        $this->pdo = $pdo;
    }

    public function addReviewType($findingId, $type)
    {
        return "INSERT INTO review_findings_type (review_finding, type) VALUES (" .
            $this->pdo->quote($findingId) .
            "," .
            $this->pdo->quote($type) .
            ");";
    }

    public function getReviewFindingsDeleteStatement($findingId)
    {
        return "DELETE FROM review_findings WHERE id=" . $this->pdo->quote($findingId) . ";";
    }

    public function getReviewFindingsTypeDelete($id)
    {
        return "DELETE FROM review_findings_type WHERE review_finding=" . $this->pdo->quote($id) . ";";
    }

    public function getFindingSnippetStatement($detector, $project, $version, $finding, $snippet, $line)
    {
        return "INSERT INTO finding_snippets (detector, project, version, finding, snippet, line) VALUES(" .
            $this->pdo->quote($detector) .
            "," .
            $this->pdo->quote($project) .
            "," .
            $this->pdo->quote($version) .
            "," .
            $this->pdo->quote($finding) .
            "," .
            $this->pdo->quote($snippet) .
            "," .
            $this->pdo->quote($line) .
            ");";
    }

    public function getMetaSnippetStatement($project, $version, $misuse, $snippet, $line)
    {
        return "INSERT INTO meta_snippets (project, version, misuse, snippet, line) VALUES(" .
            $this->pdo->quote($project) .
            "," .
            $this->pdo->quote($version) .
            "," .
            $this->pdo->quote($misuse) .
            "," .
            $this->pdo->quote($snippet) .
            "," .
            $this->pdo->quote($line) .
            ");";
    }

    public function getReviewStatement($exp, $detector, $project, $version, $misuse, $name, $comment)
    {
        return "INSERT INTO reviews (exp, detector, project, version, misuse, name, comment) VALUES (" .
            $this->pdo->quote($exp) .
            "," .
            $this->pdo->quote($detector) .
            "," .
            $this->pdo->quote($project) .
            "," .
            $this->pdo->quote($version) .
            "," .
            $this->pdo->quote($misuse) .
            "," .
            $this->pdo->quote($name) .
            "," .
            $this->pdo->quote($comment) .
            ");";
    }

    public function getReviewDeleteStatement($exp, $detector, $project, $version, $misuse, $name)
    {
        return "DELETE FROM reviews WHERE exp=" .
            $this->pdo->quote($exp) .
            " AND detector=" .
            $this->pdo->quote($detector) .
            " AND project=" .
            $this->pdo->quote($project) .
            " AND version=" .
            $this->pdo->quote($version) .
            " AND misuse=" .
            $this->pdo->quote($misuse) .
            " AND name=" .
            $this->pdo->quote($name) .
            ";";
    }

    public function deleteStatement($table, $project, $version)
    {
        return "DELETE FROM " . $table . " WHERE identifier=" . $this->pdo->quote($project . "." . $version) . ";";
    }

    public function columnQuery($table)
    {
        return "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=" . $this->pdo->quote($table) . ";";
    }

    public function getReviewFindingStatement($reviewId, $decision, $rank)
    {
        return "INSERT INTO review_findings (decision, review, rank) VALUES(" .
            $this->pdo->quote($decision) .
            ", " .
            $this->pdo->quote($reviewId) .
            "," .
            $this->pdo->quote($rank) .
            ");";
    }

    public function deleteMetadata($misuse)
    {
        return "DELETE FROM metadata WHERE misuse='" . $misuse . "';";
    }

    public function insertMetadata($project, $version, $misuse, $desc, $fix_desc, $diff_url, $violation, $file, $method)
    {
        return "INSERT INTO metadata (project, version, misuse, description, fix_description, diff_url, violation_types, file, method) VALUES(" .
            $this->pdo->quote($project) .
            "," .
            $this->pdo->quote($version) .
            "," .
            $this->pdo->quote($misuse) .
            "," .
            $this->pdo->quote($desc) .
            "," .
            $this->pdo->quote($fix_desc) .
            "," .
            $this->pdo->quote($diff_url) .
            "," .
            $this->pdo->quote($violation) .
            "," .
            $this->pdo->quote($file) .
            "," .
            $this->pdo->quote($method) .
            ");";
    }

    public function insertPattern($misuse, $id, $code, $line)
    {
        return "INSERT INTO patterns (misuse, name, code, line) VALUES(" .
            $this->pdo->quote($misuse) .
            "," .
            $this->pdo->quote($id) .
            "," .
            $this->pdo->quote($code) .
            "," .
            $this->pdo->quote($line) .
            ");";
    }

    public function deletePatterns($misuse)
    {
        return "DELETE FROM patterns WHERE misuse=" . $this->pdo->quote($misuse) . ";";
    }

    public function getStatStatement($table, $project, $version, $result, $runtime, $findings, $exp)
    {
        return "INSERT INTO stats (exp, detector, project, version, result, runtime, number_of_findings) VALUES (" .
            $this->pdo->quote($exp) .
            "," .
            $this->pdo->quote($table) .
            "," .
            $this->pdo->quote($project) .
            "," .
            $this->pdo->quote($version) .
            "," .
            $this->pdo->quote($result) .
            "," .
            $this->pdo->quote($runtime) .
            "," .
            $this->pdo->quote($findings) .
            ");";
    }

    public function getStatDeleteStatement($exp, $detector, $project, $version)
    {
        return "DELETE FROM stats WHERE exp=" .
            $this->pdo->quote($exp) .
            " AND detector=" .
            $this->pdo->quote($detector) .
            " AND project=" .
            $this->pdo->quote($project) .
            " AND version=" .
            $this->pdo->quote($version) .
            ";";
    }

    public function createTableStatement($name, $obj)
    {
        // exp project version misuse rank (AUTO INCREMENT id)
        $output = 'CREATE TABLE ' .
            $name .
            '(exp VARCHAR(100) NOT NULL, project VARCHAR(100) NOT NULL, version VARCHAR(100) NOT NULL, misuse VARCHAR(100) NOT NULL';
        if($obj) {
            foreach ($obj[0] as $key => $value) {
                if ($key === "id" || $key === "misuse" || $key === "target_snippets") {
                    continue;
                } else if ($key === "rank") {
                    $output = $output . "," . $key . " VARCHAR(100)";
                } else {
                    $output = $output . "," . $key . " TEXT";
                }
            }
        }
        $output = $output . ', PRIMARY KEY(exp, project, version, misuse, rank));';
        return $output;
    }

    public function addColumnStatement($table, $column)
    {
        return 'ALTER TABLE ' . $table . ' ADD ' . $column . ' TEXT;';
    }

    public function insertStatement($table, $exp, $project, $version, $obj)
    {
        $output = "INSERT INTO " . $table . " ( exp, project, version, misuse";
        $values = " VALUES (" .
            $this->pdo->quote($exp) .
            "," .
            $this->pdo->quote($project) .
            "," .
            $this->pdo->quote($version) .
            "," .
            $this->pdo->quote($exp !== "ex2" ? $obj->{'misuse'} : $obj->{'rank'});
        foreach ($obj as $key => $value) {
            if ($key === "id" || $key === "misuse" || $key === "target_snippets") {
                continue;
            } else {
                $output = $output . ", " . $key;
                $values = $values . "," . $this->pdo->quote(is_array($value) ? $this->arrayToString($value) : $value);
            }
        }

        $output = $output . ")";
        $values = $values . ");";
        $output = $output . $values;
        return $output;
    }

    public function arrayToString($json)
    {
        $out = $json[0];
        for ($i = 1; $i < count($json); $i++) {
            $out = $out . ';' . $json[$i];
        }
        return $out;
    }

}