<?php
use Monolog\Logger;

class SnippetUploader
{

    private $db;
    private $logger;
    private $query;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
        $this->logger = $logger;
    }

    public function processSnippet($obj){
        $this->handleTargetSnippets($this->db->getTableName($obj['detector']), $obj['project'], $obj['version'], $obj['misuse'], $obj['snippet'], $obj['line']);
    }

    private function handleTargetSnippets($detector, $project, $version, $finding, $snippet, $line){
        if(!$snippet){
            return;
        }
        $this->logger->info("saving snippet for " . $detector . "|" . $project . "|" . $version . "|" . $finding);
        $this->db->execStatement($this->getFindingSnippetStatement($detector, $project, $version, $finding, $snippet, $line));
    }

    private function getFindingSnippetStatement($detector, $project, $version, $finding, $snippet, $line)
    {
        return "INSERT INTO finding_snippets (detector, project, version, finding, snippet, line) VALUES(" .
            $this->db->quote($detector) .
            "," .
            $this->db->quote($project) .
            "," .
            $this->db->quote($version) .
            "," .
            $this->db->quote($finding) .
            "," .
            $this->db->quote($snippet) .
            "," .
            $this->db->quote($line) .
            ");";
    }
}