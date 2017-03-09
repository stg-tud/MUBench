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

    public function processData($ex, $run)
    {
        $detector = $run->{'detector'};
        $table = $this->db->getTableName($detector);
        $this->logger->info("Data for : " . $table);
        $project = $run->{'project'};
        $version = $run->{'version'};
        $runtime = $run->{'runtime'};
        $result = $run->{'result'};
        $number_of_findings = $run->{'number_of_findings'};
        $potential_hits = $run->{'potential_hits'};

        $this->updateRunStatistics($table, $ex, $project, $version, $result, $runtime, $number_of_findings);
        if($potential_hits) {
            $this->createOrUpdateFindingsTable($table, $potential_hits);
            $this->storeFindings($table, $ex, $project, $version, $potential_hits);
        }
    }

    private function updateRunStatistics($table, $exp, $project, $version, $result, $runtime, $number_of_findings)
    {
        $this->logger->info("Update statistics for $exp, $table, $project, $version");
        $this->deleteOldRunStatistics($table, $exp, $project, $version);
        $this->insertRunStatistics($table, $exp, $project, $version, $result, $runtime, $number_of_findings);
    }

    private function deleteOldRunStatistics($table, $exp, $project, $version)
    {
        $this->db->execStatement("DELETE FROM `stats` WHERE `exp` = " . $this->db->quote($exp) .
            " AND `detector` = " . $this->db->quote($table) .
            " AND `project` = " . $this->db->quote($project) .
            " AND `version` = " . $this->db->quote($version));
    }

    private function insertRunStatistics($table, $exp, $project, $version, $result, $runtime, $number_of_findings)
    {
        $this->db->execStatement("INSERT INTO `stats` (`exp`, `detector`, `project`, `version`, `result`, `runtime`, `number_of_findings`) VALUES (" .
            $this->db->quote($exp) . "," .
            $this->db->quote($table) . "," .
            $this->db->quote($project) . "," .
            $this->db->quote($version) . "," .
            $this->db->quote($result) . "," .
            $this->db->quote($runtime) . "," .
            $this->db->quote($number_of_findings) . ")");
    }

    private function createOrUpdateFindingsTable($table, $findings)
    {
        $columns = $this->db->getTableColumns($table);
        if (count($columns) == 0) {
            $this->createFindingsTable($table);
            $columns = $this->db->getTableColumns($table);
        }
        $this->logger->info("Add columns to findings table " . $table);
        foreach ($this->getFindingsPropertyNames($findings) as $property) {
            if (!in_array($property, $columns)) {
                $this->addColumnToFindingsTable($table, $property);
            }
        }
    }

    private function createFindingsTable($table)
    {
        $this->logger->info("Create findings table " . $table);
        $this->db->execStatement("CREATE TABLE `$table` (`exp` VARCHAR(100) NOT NULL, `project` VARCHAR(100) NOT NULL," .
            " `version` VARCHAR(100) NOT NULL, `misuse` VARCHAR(100) NOT NULL, `rank` VARCHAR(100) NOT NULL," .
            " PRIMARY KEY(`exp`, `project`, `version`, `misuse`, `rank`))");
    }

    private function getFindingsPropertyNames($findings)
    {
        $properties = [];
        foreach ($findings as $finding) {
            $properties = array_merge($properties, array_fill_keys(array_keys(get_object_vars($finding)), 1));
        }
        unset($properties["id"]);
        unset($properties["target_snippets"]);
        return array_keys($properties);
    }

    private function addColumnToFindingsTable($table, $column)
    {
        $this->db->execStatement("ALTER TABLE `$table` ADD `$column` TEXT");
    }

    private function storeFindings($table, $exp, $project, $version, $findings)
    {
        $this->logger->info("Store " . count($findings) . " findings in $table");
        foreach ($findings as $finding) {
            $this->storeFinding($table, $exp, $project, $version, $finding);
            if(strcmp($exp, "ex2") === 0){
                $this->storeFindingTargetSnippets($table, $project, $version, $finding->{'rank'}, $finding->{'target_snippets'});
            }
        }
    }

    private function storeFinding($table, $exp, $project, $version, $finding)
    {
        $values = array("exp" => $exp, "project" => $project, "version" => $version);
        foreach ($this->getFindingsPropertyNames([$finding]) as $property) {
            $value = $finding->{$property};
            $values[$property] = is_array($value) ? $this->arrayToString($value) : $value;
        }
        if ($exp === "ex2") {
            $values["misuse"] = $finding->{'rank'};
        }
        $values = array_map(function ($value) { return $this->db->quote($value); }, $values);
        $this->db->execStatement("INSERT INTO `" . $table .
            "` (`" . implode("`, `", array_keys($values)) . "`)" .
            " VALUES (" . implode(", ", $values) . ")");
    }

    private function arrayToString($array)
    {
        return implode(";", $array);
    }

    private function storeFindingTargetSnippets($detector, $project, $version, $rank, $snippets){
        $this->logger->info("Store " . count($snippets) . " snippets for $detector, $project, $version, $rank");
        foreach($snippets as $snippet){
            $this->storeFindingTargetSnippet($detector, $project, $version, $rank, $snippet->{'code'}, $snippet->{'first_line_number'});
        }
    }

    public function storeFindingTargetSnippet($detector, $project, $version, $rank, $snippet, $first_line_number)
    {
        $this->db->execStatement("INSERT INTO `finding_snippets` (`detector`, `project`, `version`, `finding`, `snippet`, `line`) VALUES (" .
            $this->db->quote($detector) . "," .
            $this->db->quote($project) . "," .
            $this->db->quote($version) . "," .
            $this->db->quote($rank) . "," .
            $this->db->quote($snippet) . "," .
            $this->db->quote($first_line_number) . ")");
    }

}
