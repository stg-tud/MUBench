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
        $runtime = $run->{'runtime'};
        $result = $run->{'result'};
        $number_of_findings = $run->{'number_of_findings'};
        $potential_hits = $run->{'potential_hits'};

        $this->createOrUpdateDetectorStatsTable($detector, $run);
        $this->deleteAndStoreStats($detector, $exp, $project, $version, $run);
        if ($potential_hits) {
            $this->createOrUpdateFindingsTable($detector, $potential_hits);
            $this->storeFindings($exp, $detector, $project, $version, $potential_hits);
        }
    }

    private function createOrUpdateDetectorStatsTable(Detector $detector, $run)
    {
        $propertyColumns = $this->getPropertyColumnNames($detector->getStatsTableName());
        if (count($propertyColumns) == 0) {
            $this->createStatsTable($detector);
            $propertyColumns = ['exp', 'project', 'version'];
        }
        $this->logger->info("Add columns to stats table" . $detector);
        $this->addColumnsToTable($detector->getStatsTableName(), $propertyColumns, [$run]);
    }

    private function createOrUpdateFindingsTable(Detector $detector, $findings)
    {
        $propertyColumns = $this->getPropertyColumnNames($detector->getTableName());
        if (count($propertyColumns) == 0) {
            $this->createFindingsTable($detector);
            $propertyColumns = ['exp', 'project', 'version', 'misuse', 'rank'];
        }
        $this->logger->info("Add columns to findings table " . $detector);
        $this->addColumnsToTable($detector->getTableName(), $propertyColumns, $findings);
    }

    private function addColumnsToTable($table_name, $property_columns, $json_object)
    {
        foreach ($this->getPropertyToColumnNameMapping($json_object) as $column) {
            if (!in_array($column, $property_columns)) {
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

    private function createFindingsTable(Detector $detector)
    {
        $this->logger->info("Create findings table for $detector");
        $this->db->create_table($detector->getTableName(), ['`exp` VARCHAR(10) NOT NULL',
            '`project` VARCHAR(255) NOT NULL', '`version` VARCHAR(255) NOT NULL', '`misuse` VARCHAR(255) NOT NULL',
            '`rank` VARCHAR(10) NOT NULL', 'PRIMARY KEY(`exp`, `project`, `version`, `misuse`, `rank`)']);
    }

    private function createStatsTable(Detector $detector)
    {
        $this->logger->info("Create stats table for $detector");
        $this->db->create_table($detector->getStatsTableName(),
            ['`exp` VARCHAR(10) NOT NULL', '`project` VARCHAR(255) NOT NULL', '`version` VARCHAR(255) NOT NULL',
                'PRIMARY KEY(`exp`, `project`, `version`)']);
    }

    private function getPropertyToColumnNameMapping($json_array)
    {
        $propertyToColumnNameMapping = [];
        foreach ($json_array as $json_object) {
            $properties = array_keys(get_object_vars($json_object));
            foreach ($properties as $property) {
                // MySQL does not permit column names with more than 64 characters:
                // https://dev.mysql.com/doc/refman/5.7/en/identifiers.html
                $column_name = strlen($property) > 64 ? substr($property, 0, 64) : $property;
                // Remove . from column names, since it may be confused with a table-qualified name.
                $column_name = str_replace('.', ':', $column_name);
                $propertyToColumnNameMapping[$property] = $column_name;
            }
        }
        unset($propertyToColumnNameMapping["id"]);
        unset($propertyToColumnNameMapping["target_snippets"]);
        unset($propertyToColumnNameMapping["potential_hits"]);
        unset($propertyToColumnNameMapping["detector"]);
        return $propertyToColumnNameMapping;
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
        foreach ($this->getPropertyToColumnNameMapping([$finding]) as $property => $column) {
            $value = $finding->{$property};
            $values[$column] = is_array($value) ? $this->arrayToString($value) : $value;
        }
        if ($exp === "ex2") {
            $values["misuse"] = $finding->{'rank'};
        }
        $this->db->table($detector->getTableName())->insert($values);
    }

    private function deleteAndStoreStats($detector, $exp, $project, $version, $run)
    {
        $this->db->table($detector->getStatsTableName())->where("exp", $exp)->where("project", $project)->where("version", $version)->delete();
        $values = array("exp" => $exp, "project" => $project, "version" => $version);
        foreach ($this->getPropertyToColumnNameMapping([$run]) as $property => $column) {
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
