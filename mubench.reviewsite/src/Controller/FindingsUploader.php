<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;
use MuBench\ReviewSite\Model\Detector;

class FindingsUploader
{

    private $db;
    private $logger;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
        $this->logger = $logger;
    }

    public function processData($exp, $run)
    {
        $detector = $this->db->getOrCreateDetector($run->{'detector'});
        $this->logger->info("Data for : " . $detector->name);
        $project = $run->{'project'};
        $version = $run->{'version'};
        $potential_hits = $run->{'potential_hits'};

        $this->createOrUpdateStatsTable($detector, $run);
        $this->deleteAndStoreStats($detector, $exp, $project, $version, $run);
        if ($potential_hits) {
            $this->createOrUpdateFindingsTable($detector, $potential_hits);
            $this->storeFindings($exp, $detector, $project, $version, $potential_hits);
        }
    }

    private function createOrUpdateStatsTable(Detector $detector, $run)
    {
        $propertyToColumnNameMapping = $this->getColumnNamesFromProperties($run);
        $propertyToColumnNameMapping = $this->removeDisruptiveStatsColumns($propertyToColumnNameMapping);
        $this->createOrUpdateTable($detector->getStatsTableName(), $propertyToColumnNameMapping, array($this, 'createStatsTable'));
    }

    private function createOrUpdateFindingsTable(Detector $detector, $findings)
    {
        $propertyToColumnNameMapping = $this->getPropertyToColumnNameMapping($findings);
        $propertyToColumnNameMapping = $this->removeDisruptiveFindingsColumns($propertyToColumnNameMapping);
        $this->createOrUpdateTable($detector->getTableName(), $propertyToColumnNameMapping, array($this, 'createFindingsTable'));
    }

    private function createOrUpdateTable($table_name, $propertyToColumnNameMapping, $createFunc)
    {
        $existing_columns = $this->getPropertyColumnNames($table_name);
        if (count($existing_columns) == 0) {
            $existing_columns = $createFunc($table_name);
        }
        $this->logger->info("Add columns to " . $table_name);
        foreach ($propertyToColumnNameMapping as $column) {
            if (!in_array($column, $existing_columns)) {
                $this->addColumnToTable($table_name, $column);
            }
        }
    }

    private function getPropertyColumnNames($table_name)
    {
        try {
            /** @noinspection PhpParamsInspection */
            return array_keys($this->db->table($table_name)->first());
        } catch (\Exception $e) {
            return []; // table does not exist (we always insert immediately after creation, so it cannot be empty)
        }
    }

    private function createFindingsTable($table_name)
    {
        $this->logger->info("Create table: " . $table_name);
        $this->db->create_table($table_name, ['`exp` VARCHAR(10) NOT NULL',
            '`project` VARCHAR(100) NOT NULL', '`version` VARCHAR(100) NOT NULL', '`misuse` VARCHAR(100) NOT NULL',
            '`rank` VARCHAR(10) NOT NULL', 'PRIMARY KEY(`exp`, `project`, `version`, `misuse`, `rank`)']);
        return ['exp', 'project', 'version', 'misuse', 'rank'];
    }

    private function createStatsTable($table_name)
    {
        $this->logger->info("Create table: " . $table_name);
        $this->db->create_table($table_name,
            ['`exp` VARCHAR(10) NOT NULL', '`project` VARCHAR(100) NOT NULL', '`version` VARCHAR(100) NOT NULL',
                'PRIMARY KEY(`exp`, `project`, `version`)']);
        return ['exp', 'project', 'version'];
    }

    private function getPropertyToColumnNameMapping($entries)
    {
        $propertyToColumnNameMapping = [];
        foreach ($entries as $entry) {
            $propertyToColumnName = $this->getColumnNamesFromProperties($entry);
            foreach($propertyToColumnName as $property => $column){
                $propertyToColumnNameMapping[$property] = $column;
            }
        }
        return $propertyToColumnNameMapping;
    }

    private function getColumnNamesFromProperties($entry)
    {
        $propertyToColumnNameMapping = [];
        $properties = array_keys(get_object_vars($entry));
        foreach ($properties as $property) {
            // MySQL does not permit column names with more than 64 characters:
            // https://dev.mysql.com/doc/refman/5.7/en/identifiers.html
            $column_name = strlen($property) > 64 ? substr($property, 0, 64) : $property;
            // Remove . from column names, since it may be confused with a table-qualified name.
            $column_name = str_replace('.', ':', $column_name);
            $propertyToColumnNameMapping[$property] = $column_name;
        }
        return $propertyToColumnNameMapping;
    }

    private function removeDisruptiveStatsColumns($columns)
    {
        unset($columns["potential_hits"]);
        unset($columns["detector"]);
        return $columns;
    }

    private function removeDisruptiveFindingsColumns($columns)
    {
        unset($columns["id"]);
        unset($columns["target_snippets"]);
        return $columns;
    }

    private function addColumnToTable($table_name, $column)
    {
        $this->db->add_column($table_name, "`$column` TEXT");
    }

    private function storeFindings($exp, Detector $detector, $project, $version, $findings)
    {
        $this->logger->info("Store " . count($findings) . " findings of $detector");
        foreach ($findings as $finding) {
            $this->storeFinding($exp, $detector, $project, $version, $finding);
            if (strcmp($exp, "ex2") === 0) {
                $this->storeFindingTargetSnippets($project, $detector, $version, $finding->{'rank'},
                    $finding->{'target_snippets'});
            }
        }
    }

    private function storeFinding($exp, Detector $detector, $project, $version, $finding)
    {
        $values = array("exp" => $exp, "project" => $project, "version" => $version);
        $propertyToColumnNameMapping = $this->getPropertyToColumnNameMapping([$finding]);
        $propertyToColumnNameMapping = $this->removeDisruptiveFindingsColumns($propertyToColumnNameMapping);
        foreach ($propertyToColumnNameMapping as $property => $column) {
            $value = $finding->{$property};
            $values[$column] = is_array($value) ? $this->arrayToString($value) : $value;
        }
        if ($exp === "ex2") {
            $values["misuse"] = $finding->{'rank'};
        }
        $this->db->table($detector->getTableName())->insert($values);
    }

    private function deleteAndStoreStats(Detector $detector, $exp, $project, $version, $run)
    {
        $this->db->table($detector->getStatsTableName())->where("exp", $exp)->where("project", $project)->where("version", $version)->delete();
        $values = array("exp" => $exp, "project" => $project, "version" => $version);
        $propertyToColumnNameMapping = $this->getColumnNamesFromProperties($run);
        $propertyToColumnNameMapping = $this->removeDisruptiveStatsColumns($propertyToColumnNameMapping);
        foreach ($propertyToColumnNameMapping as $property => $column) {
            $value = $run->{$property};
            $values[$column] = is_array($value) ? $this->arrayToString($value) : $value;
        }
        $this->db->table($detector->getStatsTableName())->insert($values);
    }

    private function arrayToString($array)
    {
        return implode(";", $array);
    }

    private function storeFindingTargetSnippets($project, Detector $detector, $version, $rank, $snippets)
    {
        $this->logger->info("Store " . count($snippets) . " snippets for $detector, $project, $version, $rank");
        foreach ($snippets as $snippet) {
            $this->db->table('finding_snippets')->insert(['detector' => $detector->id, 'project' => $project,
                'version' => $version, 'finding' => $rank, 'snippet' => $snippet->{'code'},
                'line' => $snippet->{'first_line_number'}]);
        }
    }

}
