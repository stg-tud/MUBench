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
        $detector = $this->db->getOrCreateDetector($finding['detector']);
        $project = $finding['project'];
        $version = $finding['version'];
        $misuse = $finding['misuse'];
        $snippet = $finding['snippet'];
        $line = $finding['line'];
        $this->logger->info("saving snippet for $detector, " . $project . ", " . $version . ", " . $misuse);
        $this->db->table('finding_snippets')->insert(['detector' => $detector->id, 'project' => $project,
            'version' => $version, 'finding' => $misuse, 'snippet' => $snippet, 'line' => $line]);
    }

    public function deleteSnippet($finding_id)
    {
        $this->logger->info("deleting snippet with id: " . $finding_id);
        $this->db->table('finding_snippets')->where('id', $finding_id)->delete();
    }
}