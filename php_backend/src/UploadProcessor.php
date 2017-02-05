<?php
require_once 'QueryBuilder.php';

use Monolog\Logger;

class UploadProcessor
{

    private $db;
    private $logger;
    private $query;

    function __construct(DBConnection $db, QueryBuilder $queryBuilder, Logger $logger)
    {
        $this->db = $db;
        $this->query = $queryBuilder;
        $this->logger = $logger;
    }

    public function processReview($review)
    {
        $name = $review['review_name'];
        $exp = $review['review_exp'];
        $detector = $review['review_detector'];
        $project = $review['review_project'];
        $version = $review['review_version'];
        $misuse = $review['review_misuse'];
        $comment = $review['review_comment'];
        $hits = $review['review_hit'];
        $statements = [];
        $oldReview = $this->db->getReview($exp, $detector, $project, $version, $misuse, $name);
        if($oldReview){
            $oldId = intval($oldReview['id']);
            $oldFindings = $this->db->getReviewFindings($oldId);
            foreach($oldFindings as $oldFinding){
                $statements[] = $this->query->getReviewFindingsDeleteStatement(intval($oldFinding['id']));
                $statements[] = $this->query->getReviewFindingsTypeDelete(intval($oldFinding['id']));
            }
        }

        $statements[] = $this->query->getReviewDeleteStatement($exp, $detector, $project, $version, $misuse, $name);
        $statements[] = $this->query->getReviewStatement($exp, $detector, $project, $version, $misuse, $name, $comment);
        $this->db->execStatements($statements);
        $newReview = $this->db->getReview($exp, $detector, $project, $version, $misuse, $name);
        if(!$newReview){
            $this->logger->error("Review not found");
            return;
        }
        $id = intval($newReview['id']);
        foreach($hits as $key => $hit){
            $this->db->execStatement($this->query->getReviewFindingStatement($id, $hit['hit'], $key));
            $findingEntry = $this->db->getReviewFinding($id, $key);
            if(!$findingEntry){
                $this->logger->error("finding not found");
                continue;
            }
            $findingId = intval($findingEntry['id']);
            foreach($hit['types'] as $type){
                $typeId = $this->db->getTypeIdByName($type);
                $this->db->execStatement($this->query->addReviewType($findingId, $typeId));
            }
        }
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
        $obj_columns = [];
        if($obj_array) {
            //$obj_array = $this->rearrangeCodeSnippets($obj_array);
            $obj_columns = $this->getJsonNames($obj_array);
        }
        $columns = $this->db->getTableColumns($table);
        $this->handleStats($table, $project, $version, $result, $runtime, $findings, $ex);
        $this->handleTableColumns($table, $obj_columns, $columns, $obj_array);
        $this->handleFindings($table, $ex, $project, $version, $obj_array);
    }

    public function handleStats($table, $project, $version, $result, $runtime, $findings, $exp)
    {
        $statements = [];
        $statements[] = $this->query->getStatDeleteStatement($exp, $table, $project, $version);
        $statements[] = $this->query->getStatStatement($table, $project, $version, $result, $runtime, $findings, $exp);
        $this->logger->info("deleting and adding new stats for: " . $table);
        $this->db->execStatements($statements);
    }

    public function handleFindings($table, $exp, $project, $version, $obj_array)
    {
        $statements = [];
        foreach ($obj_array as $hit) {
            $statements[] = $this->query->insertStatement($table, $exp, $project, $version, $hit);
            $this->handleTargetSnippets($table, $project, $version, strcmp($exp, "ex2") !== 0 ? $hit->{'misuse'} : $hit->{'rank'}, $hit->{'target_snippets'});
        }
        $this->logger->info("inserting " . count($statements) . " entries into: " . $table);
        $this->db->execStatements($statements);
    }

    public function handleTargetSnippets($detector, $project, $version, $finding, $snippets){
        $statements = [];
        if(!$snippets || !is_array($snippets)){
            return;
        }
        foreach($snippets as $key => $snippet){
            $statements[] = $this->query->getFindingSnippetStatement($detector, $project, $version, $finding, $snippet->{'code'}, $snippet->{'first_line_number'});
        }
        $this->logger->info("saving " . count($statements) . " for " . $detector . "|" . $project . "|" . $version . "|" . $finding);
        $this->db->execStatements($statements);
    }

    public function handleTableColumns($table, $obj_columns, $columns, $obj_array)
    {
        $statements = [];
        if (count($columns) == 0) {
            $this->logger->info("Creating new table " . $table);
            $statements[] = $this->query->createTableStatement($table, $obj_array);
            $this->db->execStatements($statements);
            return;
        }
        if(!$obj_columns){
            return;
        }
        //$statements[] = $this->db->deleteStatement($table, $project, $version);
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
                $statements[] = $this->query->addColumnStatement($table, $c);
            }
        }
        $this->logger->info("deleting and adding columns for: " . $table);
        $this->db->execStatements($statements);
    }

    public function processMetaData($json)
    {
        $project = $json->{'project'};
        $version = $json->{'version'};
        $misuse = $json->{'misuse'};
        $statements = [];
        $statements[] = $this->query->deleteMetadata($json->{'misuse'});
        $statements[] = $this->query->deletePatterns($json->{'misuse'});
        $statements[] =
            $this->query->insertMetadata($project, $version, $misuse, $json->{'description'}, $json->{'fix'}->{'description'},
                $json->{'fix'}->{'diff-url'}, $this->arrayToString($json->{'violation_types'}),
                $json->{'location'}->{'file'}, $json->{'location'}->{'method'});
        foreach ($json->{'patterns'} as $p) {
            $statements[] = $this->query->insertPattern($misuse, $p->{'id'}, $p->{'snippet'}->{'code'},
                $p->{'snippet'}->{'first_line'});
        }
        if($json->{'target_snippets'}) {
            foreach ($json->{'target_snippets'} as $snippet) {
                $statements[] = $this->query->getMetaSnippetStatement($project, $version, $misuse, $snippet->{'code'},
                    $snippet->{'first_line_number'});
            }
        }
        $this->db->execStatements($statements);
    }

    public function arrayToString($json)
    {
        $out = $json[0];
        for ($i = 1; $i < count($json); $i++) {
            $out = $out . ';' . $json[$i];
        }
        return $out;
    }

    public function getJsonNames($obj)
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

}