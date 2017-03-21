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

        $this->updateRunStatistics($exp, $detector, $project, $version, $result, $runtime, $number_of_findings);
        if($potential_hits) {
            $this->createOrUpdateFindingsTable($detector, $potential_hits);
            $this->storeFindings($exp, $detector, $project, $version, $potential_hits);
        }
    }

    private function updateRunStatistics($exp, Detector $detector, $project, $version, $result, $runtime, $number_of_findings)
    {
        $this->logger->info("Update statistics for $exp, $detector, $project, $version");
        $this->deleteOldRunStatistics($exp, $detector, $project, $version);
        $this->insertRunStatistics($exp, $detector, $project, $version, $result, $runtime, $number_of_findings);
    }

    private function deleteOldRunStatistics($exp, Detector $detector, $project, $version)
    {
        $this->db->table('stats')->where('exp', $exp)->where('detector', $detector->id)
            ->where('project', $project)->where('version', $version)->delete();
    }

    private function insertRunStatistics($exp, Detector $detector, $project, $version, $result, $runtime, $number_of_findings)
    {
        $this->db->table('stats')->insert(['exp' => $exp, 'detector' => $detector->id, 'project' => $project,
            'version' => $version, 'result' => $result, 'runtime' => $runtime,
            'number_of_findings' => $number_of_findings]);
    }

    private function createOrUpdateFindingsTable(Detector $detector, $findings)
    {
        $propertyColumns = $this->getDetectorFindingPropertyColumnNames($detector);
        if (count($propertyColumns) == 0) {
            $this->createFindingsTable($detector);
            $propertyColumns = ['exp', 'project', 'version', 'misuse', 'rank'];
        }
        $this->logger->info("Add columns to findings table " . $detector);
        foreach ($this->getPropertyToColumnNameMapping($findings) as $column) {
            if (!in_array($column, $propertyColumns)) {
                $this->addColumnToFindingsTable($detector, $column);
            }
        }
    }

    private function getDetectorFindingPropertyColumnNames(Detector $detector)
    {
        try {
            /** @noinspection PhpParamsInspection */
            return array_keys($this->db->table($detector->getTableName())->first());
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

    private function getPropertyToColumnNameMapping($findings)
    {
        $propertyToColumnNameMapping = [];
        foreach ($findings as $finding) {
            $properties = array_keys(get_object_vars($finding));
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
        return $propertyToColumnNameMapping;
    }

    private function addColumnToFindingsTable(Detector $detector, $column)
    {
        $this->db->add_column($detector->getTableName(), "`$column` TEXT");
    }

    private function storeFindings($exp, Detector $detector, $project, $version, $findings)
    {
        $this->logger->info("Store " . count($findings) . " findings of $detector");
        foreach ($findings as $finding) {
            $this->storeFinding($exp, $detector, $project, $version, $finding);
            if(strcmp($exp, "ex2") === 0){
                $this->storeFindingTargetSnippets($project, $detector, $version, $finding->{'rank'}, $finding->{'target_snippets'});
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

    private function arrayToString($array)
    {
        return implode(";", $array);
    }

    private function storeFindingTargetSnippets($project, Detector $detector, $version, $rank, $snippets){
        $this->logger->info("Store " . count($snippets) . " snippets for $detector, $project, $version, $rank");
        foreach($snippets as $snippet) {
            $this->db->table('finding_snippets')->insert(['detector' => $detector->id, 'project' => $project,
                'version' => $version, 'finding' => $rank, 'snippet' => $snippet->{'code'},
                'line' => $snippet->{'first_line_number'}]);
        }
    }

}
