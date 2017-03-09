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
        foreach ($this->getPropertyToColumnNameMapping($findings) as $column) {
            if (!in_array($column, $columns)) {
                $this->addColumnToFindingsTable($table, $column);
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

    private function getPropertyToColumnNameMapping($findings)
    {
        $propertyToColumnNameMapping = [];
        foreach ($findings as $finding) {
            $properties = array_keys(get_object_vars($finding));
            foreach ($properties as $property) {
                // MySQL does not permit column names with more than 64 characters:
                // https://dev.mysql.com/doc/refman/5.7/en/identifiers.html
                $column_name = strlen($property) > 64 ? substr($property, 0, 64) : $property;
                $propertyToColumnNameMapping[$property] = $column_name;
            }
        }
        unset($propertyToColumnNameMapping["id"]);
        unset($propertyToColumnNameMapping["target_snippets"]);
        return $propertyToColumnNameMapping;
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
        foreach ($this->getPropertyToColumnNameMapping([$finding]) as $property => $column) {
            $value = $finding->{$property};
            $values[$column] = is_array($value) ? $this->arrayToString($value) : $value;
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
