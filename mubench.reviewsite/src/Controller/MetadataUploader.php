<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;

class MetadataUploader
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
        $statements = [];
        $statements[] = $this->deleteMetadata($json->{'misuse'});
        $statements[] = $this->deletePatterns($json->{'misuse'});
        $statements[] =
            $this->insertMetadata($project, $version, $misuse, $json->{'description'}, $json->{'fix'}->{'description'},
                $json->{'fix'}->{'diff-url'}, $this->arrayToString($json->{'violation_types'}),
                $json->{'location'}->{'file'}, $json->{'location'}->{'method'});
        foreach ($json->{'patterns'} as $p) {
            $statements[] = $this->insertPattern($misuse, $p->{'id'}, $p->{'snippet'}->{'code'},
                $p->{'snippet'}->{'first_line'});
        }
        if($json->{'target_snippets'}) {
            foreach ($json->{'target_snippets'} as $snippet) {
                $statements[] = $this->getMetaSnippetStatement($project, $version, $misuse, $snippet->{'code'},
                    $snippet->{'first_line_number'});
            }
        }
        $this->db->execStatements($statements);
    }

    private function deleteMetadata($misuse)
    {
        return "DELETE FROM metadata WHERE misuse='" . $misuse . "';";
    }

    private function deletePatterns($misuse)
    {
        return "DELETE FROM patterns WHERE misuse=" . $this->db->quote($misuse) . ";";
    }

    private function insertMetadata($project, $version, $misuse, $desc, $fix_desc, $diff_url, $violation, $file, $method)
    {
        return "INSERT INTO metadata (project, version, misuse, description, fix_description, diff_url, violation_types, file, method) VALUES(" .
            $this->db->quote($project) .
            "," .
            $this->db->quote($version) .
            "," .
            $this->db->quote($misuse) .
            "," .
            $this->db->quote($desc) .
            "," .
            $this->db->quote($fix_desc) .
            "," .
            $this->db->quote($diff_url) .
            "," .
            $this->db->quote($violation) .
            "," .
            $this->db->quote($file) .
            "," .
            $this->db->quote($method) .
            ");";
    }

    private function insertPattern($misuse, $id, $code, $line)
    {
        return "INSERT INTO patterns (misuse, name, code, line) VALUES(" .
            $this->db->quote($misuse) .
            "," .
            $this->db->quote($id) .
            "," .
            $this->db->quote($code) .
            "," .
            $this->db->quote($line) .
            ");";
    }

    private function getMetaSnippetStatement($project, $version, $misuse, $snippet, $line)
    {
        return "INSERT INTO meta_snippets (project, version, misuse, snippet, line) VALUES(" .
            $this->db->quote($project) .
            "," .
            $this->db->quote($version) .
            "," .
            $this->db->quote($misuse) .
            "," .
            $this->db->quote($snippet) .
            "," .
            $this->db->quote($line) .
            ");";
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