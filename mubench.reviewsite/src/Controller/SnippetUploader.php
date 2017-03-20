<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;

class SnippetUploader
{

    private $db;
    private $logger;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
        $this->logger = $logger;
    }

    public function processSnippet($finding){
        if (!$finding["snippet"]) {
            return;
        }
        $detector_table = $this->db->getTableName($finding['detector']);
        $this->logger->info("saving snippet for " . $finding['detector'] . ", " . $finding['project'] . ", " . $finding['version'] . ", " . $finding['misuse']);
        $this->db->table('finding_snippets')->insert(['detector' => $detector_table,
            'project' => $finding['project'], 'version' => $finding['version'], 'finding' => $finding['misuse'],
            'snippet' => $finding['snippet'], 'line' => $finding['line']]);
    }
}