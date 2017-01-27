<?php

use Monolog\Logger;

class UploadProcessor
{

    private $db;
    private $logger;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
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
                $statements[] = $this->db->getReviewFindingsDeleteStatement(intval($oldFinding['id']));
                $statements[] = $this->db->getReviewFindingsTypeDelete(intval($oldFinding['id']));
            }
        }

        $statements[] = $this->db->getReviewDeleteStatement($exp, $detector, $project, $version, $misuse, $name);
        $statements[] = $this->db->getReviewStatement($exp, $detector, $project, $version, $misuse, $name, $comment);
        $this->db->execStatements($statements);
        $newReview = $this->db->getReview($exp, $detector, $project, $version, $misuse, $name);
        if(!$newReview){
            $this->logger->error("Review not found");
            return;
        }
        $id = intval($newReview['id']);
        foreach($hits as $key => $hit){
            $this->db->execStatement($this->db->getReviewFindingStatement($id, $hit['hit'], $key));
            $findingEntry = $this->db->getReviewFinding($id, $key);
            if(!$findingEntry){
                $this->logger->error("finding not found");
                continue;
            }
            $findingId = intval($findingEntry['id']);
            foreach($hit['types'] as $type){
                $typeId = $this->db->getTypeIdByName($type);
                $this->db->execStatement($this->db->addReviewType($findingId, $typeId));
            }
        }
    }

    public function processData($ex, $obj, $obj_array)
    {
        $table = $this->db->getTableName($obj->{'detector'});
        $this->logger->info("Data for : " . $table);
        $project = $obj->{'project'};
        $version = $obj->{'version'};
        $runtime = $obj->{'runtime'};
        $result = $obj->{'result'};
        $findings = $obj->{'number_of_findings'};
        if(obj_array) {
            $obj_array = $this->rearrangeCodeSnippets($obj_array);
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
        $statements[] = $this->db->getStatDeleteStatement($exp, $table, $project, $version);
        $statements[] = $this->db->getStatStatement($table, $project, $version, $result, $runtime, $findings, $exp);
        $this->logger->info("deleting and adding new stats for: " . $table);
        $this->db->execStatements($statements);
    }

    public function handleFindings($table, $exp, $project, $version, $obj_array)
    {
        $statements = [];
        foreach ($obj_array as $hit) {
            $statements[] = $this->db->insertStatement($table, $exp, $project, $version, $hit);
        }
        $this->logger->info("inserting " . count($statements) . " entries into: " . $table);
        $this->db->execStatements($statements);
    }

    public function rearrangeCodeSnippets($obj)
    {
        foreach ($obj as $hit) {
            $code = $hit->{'target_snippets'};
            $hit->{'line'} = $code[0]->{'first_line_number'};
            $hit->{'target_snippets'} = $code[0]->{'code'};
        }
        return $obj;
    }

    public function handleTableColumns($table, $obj_columns, $columns, $obj_array)
    {
        $statements = [];
        if (count($columns) == 0) {
            $this->logger->info("Creating new table " . $table);
            $statements[] = $this->db->createTableStatement($table, $obj_array);
            $this->db->execStatements($statements);
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
                $statements[] = $this->db->addColumnStatement($table, $c);
            }
        }
        $this->logger->info("deleting and adding columns for: " . $table);
        $this->db->execStatements($statements);
    }

    public function processMetaData($json)
    {
        $statements = [];
        $statements[] = $this->db->deleteMetadata($json->{'misuse'});
        $statements[] = $this->db->deletePatterns($json->{'misuse'});
        $statements[] =
            $this->db->insertMetadata($json->{'project'}, $json->{'version'}, $json->{'misuse'}, $json->{'description'}, $json->{'fix'}->{'description'},
                $json->{'fix'}->{'diff-url'}, $this->arrayToString($json->{'violation_types'}),
                $json->{'location'}->{'file'}, $json->{'location'}->{'method'});
        foreach ($json->{'patterns'} as $p) {
            $statements[] = $this->db->insertPattern($json->{'misuse'}, $p->{'id'}, $p->{'snippet'}->{'code'},
                $p->{'snippet'}->{'first_line'});
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
            $columns[] = $key;
        }
        return $columns;
    }

}