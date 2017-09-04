<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;

class MetadataController
{

    private $db;
    private $logger;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
        $this->logger = $logger;
    }

    public function processMetaData($json)
    {
        $project = $json->{'project'};
        $version = $json->{'version'};
        $misuse = $json->{'misuse'};
        $this->deleteMetadata($json->{'misuse'});
        $this->deletePatterns($json->{'misuse'});
        $this->logger->info("saving metadata for $project, $version, $misuse");
        $this->insertMetadata($project, $version, $misuse, $json->{'description'}, $json->{'fix'}->{'description'},
            $json->{'fix'}->{'diff-url'}, $json->{'location'}->{'file'}, $json->{'location'}->{'method'});
        $this->addViolationTypesToMisuse($project, $version, $misuse, $json->{'violation_types'});

        foreach ($json->{'patterns'} as $p) {
            $this->insertPattern($misuse, $p->{'id'}, $p->{'snippet'}->{'code'}, $p->{'snippet'}->{'first_line'});
        }
        if($json->{'target_snippets'}) {
            foreach ($json->{'target_snippets'} as $snippet) {
                $this->getMetaSnippetStatement($project, $version, $misuse, $snippet->{'code'}, $snippet->{'first_line_number'});
            }
        }
    }

    private function deleteMetadata($misuse)
    {
        $this->db->table('metadata')->where('misuse', $misuse)->delete();
    }

    private function deletePatterns($misuse)
    {
        $this->db->table('patterns')->where('misuse', $misuse)->delete();
    }

    private function insertMetadata($project, $version, $misuse, $desc, $fix_desc, $diff_url, $file, $method)
    {
        $this->db->table('metadata')->insert(['project' => $project, 'version' => $version, 'misuse' => $misuse,
            'description' => $desc, 'fix_description' => $fix_desc, 'diff_url' => $diff_url, 'file' => $file, 'method' => $method]);
    }

    private function addViolationTypesToMisuse($project, $version, $misuse, $violation_types)
    {
        $this->logger->info("saving violation types for misuse");
        foreach($violation_types as $type_name){
            $violation_type = $this->getOrCreateViolationType($type_name);
            $this->logger->info(print_r($violation_type, true));
            $this->db->table('misuse_types')->insert(['project' => $project, 'version' => $version, 'misuse' => $misuse, 'type' => $violation_type['id']]);
        }
    }

    private function getOrCreateViolationType($violation_type)
    {
        $type = $this->db->table('types')->where('name', $violation_type)->first();
        if(!$type) {
            $this->db->table('types')->insert(['name' => $violation_type]);
            $type = $this->db->table('types')->where('name', $violation_type)->first();
        }
        return $type;
    }

    private function insertPattern($misuse, $id, $code, $line)
    {
        $this->db->table('patterns')->insert(['misuse' => $misuse, 'name' => $id, 'code' => $code, 'line' => $line]);
    }

    private function getMetaSnippetStatement($project, $version, $misuse, $snippet, $line)
    {
        $this->db->table('meta_snippets')->insert(['project' => $project, 'version' => $version, 'misuse' => $misuse,
            'snippet' => $snippet, 'line' => $line]);
    }

    private function arrayToString($json)
    {
        $out = $json[0];
        for ($i = 1; $i < count($json); $i++) {
            $out = $out . ';' . $json[$i];
        }
        return $out;
    }

}