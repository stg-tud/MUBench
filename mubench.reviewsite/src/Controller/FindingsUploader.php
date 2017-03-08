<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;

class FindingsUploader
{

    private $db;
    private $logger;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
        $this->logger = $logger;
    }

    public function processData($ex, $obj, $obj_array)
    {
        $detector = $obj->{'detector'};
        $table = $this->db->getTableName($detector);
        $this->logger->info("Data for : " . $table);
        $project = $obj->{'project'};
        $version = $obj->{'version'};
        $runtime = $obj->{'runtime'};
        $result = $obj->{'result'};
        $findings = $obj->{'number_of_findings'};

        $this->handleStats($table, $project, $version, $result, $runtime, $findings, $ex);
        if($obj_array) {

            $this->handleTableColumns($table, $obj_array);
            $this->handleFindings($table, $ex, $project, $version, $obj_array);
        }
    }

    private function handleStats($table, $project, $version, $result, $runtime, $findings, $exp)
    {
        $statements = [];
        $statements[] = $this->getStatDeleteStatement($exp, $table, $project, $version);
        $statements[] = $this->getStatStatement($table, $project, $version, $result, $runtime, $findings, $exp);
        $this->logger->info("deleting and adding new stats for: " . $table);
        $this->db->execStatements($statements);
    }

    private function handleFindings($table, $exp, $project, $version, $obj_array)
    {
        $statements = [];
        foreach ($obj_array as $hit) {
            $statements[] = $this->insertStatement($table, $exp, $project, $version, $hit);
            if(strcmp($exp, "ex2") === 0){
                $this->handleTargetSnippets($table, $project, $version, strcmp($exp, "ex2") !== 0 ? $hit->{'misuse'} : $hit->{'rank'}, $hit->{'target_snippets'});
            }
        }
        $this->logger->info("inserting " . count($statements) . " entries into: " . $table);
        $this->db->execStatements($statements);
    }

    private function handleTargetSnippets($detector, $project, $version, $finding, $snippets){
        $statements = [];
        if(!$snippets || !is_array($snippets)){
            return;
        }
        foreach($snippets as $key => $snippet){
            $statements[] = $this->getFindingSnippetStatement($detector, $project, $version, $finding, $snippet->{'code'}, $snippet->{'first_line_number'});
        }
        $this->logger->info("saving " . count($statements) . " for " . $detector . "|" . $project . "|" . $version . "|" . $finding);
        $this->db->execStatements($statements);
    }

    private function handleTableColumns($table, $obj_array)
    {
        $obj_columns = $this->getJsonNames($obj_array);
        $columns = $this->db->getTableColumns($table);
        $statements = [];
        if (count($columns) == 0) {
            $this->logger->info("Creating new table " . $table);
            $statements[] = $this->createTableStatement($table, $obj_array);
            $this->db->execStatements($statements);
            return;
        }
        if(!$obj_columns){
            return;
        }
        $columns = $this->db->getTableColumns($table);
        foreach ($obj_columns as $c) {
            $add = true;
            foreach ($columns as $oc) {
                if ($c == $oc) {
                    $add = false;
                    break;
                }
            }
            if ($add) {
                $statements[] = $this->addColumnStatement($table, $c);
            }
        }
        $this->logger->info("deleting and adding columns for: " . $table);
        $this->db->execStatements($statements);
    }

    private function getJsonNames($obj)
    {
        $columns = array();
        $columns[] = 'project';
        $columns[] = 'version';
        foreach ($obj[0] as $key => $value) {
            if($key === "target_snippets")
                continue;
            $columns[] = $key;
        }
        return $columns;
    }

    private function getStatDeleteStatement($exp, $detector, $project, $version)
    {
        return "DELETE FROM `stats` WHERE `exp` = " . $this->db->quote($exp) .
            " AND `detector` = " . $this->db->quote($detector) .
            " AND `project` = " . $this->db->quote($project) .
            " AND `version` = " . $this->db->quote($version);
    }

    private function getStatStatement($table, $project, $version, $result, $runtime, $findings, $exp)
    {
        return "INSERT INTO `stats` (`exp`, `detector`, `project`, `version`, `result`, `runtime`, `number_of_findings`) VALUES (" .
            $this->db->quote($exp) . "," .
            $this->db->quote($table) . "," .
            $this->db->quote($project) . "," .
            $this->db->quote($version) . "," .
            $this->db->quote($result) . "," .
            $this->db->quote($runtime) . "," .
            $this->db->quote($findings) . ")";
    }

    private function insertStatement($table, $exp, $project, $version, $obj)
    {
        $misuse = $exp !== "ex2" ? $obj->{'misuse'} : $obj->{'rank'};

        $columns = array("exp", "project", "version", "misuse");
        $values = array($exp, $project, $version, $misuse);
        foreach ($obj as $key => $value) {
            if ($key === "id" || $key === "misuse" || $key === "target_snippets") {
                continue;
            } else {
                $columns[] = $key;
                $values[] = is_array($value) ? $this->arrayToString($value) : $value;
            }
        }

        $values = array_map(function ($value) { return $this->db->quote($value); }, $values);
        return "INSERT INTO `" . $table . "` (`" . implode("`, `", $columns) . "`) VALUES (" . implode(", ", $values) . ")";
    }

    private function arrayToString($json)
    {
        $out = $json[0];
        for ($i = 1; $i < count($json); $i++) {
            $out = $out . ';' . $json[$i];
        }
        return $out;
    }

    public function getFindingSnippetStatement($detector, $project, $version, $finding, $snippet, $line)
    {
        return "INSERT INTO `finding_snippets` (`detector`, `project`, `version`, `finding`, `snippet`, `line`) VALUES (" .
            $this->db->quote($detector) . "," .
            $this->db->quote($project) . "," .
            $this->db->quote($version) . "," .
            $this->db->quote($finding) . "," .
            $this->db->quote($snippet) . "," .
            $this->db->quote($line) . ")";
    }

    public function createTableStatement($name, $potential_hits)
    {
        // exp project version misuse rank (AUTO INCREMENT id)
        $output = "CREATE TABLE `" . $name . "` (`exp` VARCHAR(100) NOT NULL, `project` VARCHAR(100) NOT NULL," .
            " `version` VARCHAR(100) NOT NULL, `misuse` VARCHAR(100) NOT NULL, `rank` VARCHAR(100) NOT NULL";
        if($potential_hits) {
            foreach ($potential_hits[0] as $key => $value) {
                if ($key === "id" || $key === "misuse" || $key === "rank" || $key === "target_snippets") {
                    continue;
                } else {
                    $output = $output . ",`" . $key . "` TEXT";
                }
            }
        }
        return $output . ', PRIMARY KEY(`exp`, `project`, `version`, `misuse`, `rank`))';
    }

    public function addColumnStatement($table, $column)
    {
        return 'ALTER TABLE `' . $table . '` ADD `' . $column . '` TEXT;';
    }

}