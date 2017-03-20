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
        $this->db->table('stats')->where('exp', $exp)->where('detector', $table)->where('project', $project)->where('version', $version)->delete();
    }

    private function insertRunStatistics($table, $exp, $project, $version, $result, $runtime, $number_of_findings)
    {
        $this->db->table('stats')->insert(['exp' => $exp, 'detector' => $table, 'project' => $project, 'version' => $version, 'result' => $result, 'runtime' => $runtime, 'number_of_findings' => $number_of_findings]);
    }

    private function createOrUpdateFindingsTable($table, $findings)
    {
        $columns = $this->db->getTableColumns($table);
        if (count($columns) == 0) {
            $this->createFindingsTable($table);
            $columns = ['exp', 'project', 'version', 'misuse', 'rank'];
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
        $this->db->create_table($table, ['`exp` VARCHAR(10) NOT NULL', '`project` VARCHAR(255) NOT NULL',
            '`version` VARCHAR(255) NOT NULL', '`misuse` VARCHAR(255) NOT NULL', '`rank` VARCHAR(10) NOT NULL',
            'PRIMARY KEY(`exp`, `project`, `version`, `misuse`, `rank`)']);
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
        $this->db->add_column($table, "`$column` TEXT");
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
        $this->db->table($table)->insert($values);
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
        $this->db->table('finding_snippets')->insert(['detector' => $detector, 'project' => $project, 'version' => $version, 'finding' => $rank, 'snippet' => $snippet, 'line' => $first_line_number]);
    }

}
