<?php

namespace MuBench\ReviewSite\Controller;

require_once "DatabaseTestCase.php";

use DatabaseTestCase;

class StoreMetadataTest extends DatabaseTestCase
{
    function test_store_metadata()
    {
        $detector = $this->db->getOrCreateDetector('-d-');
        $metadataController = new MetadataController($this->db, $this->logger);

        $metadataController->updateMetadata('-m-', '-p-', '-v-', '-desc-',
            ['diff-url' => '-diff-', 'description' => '-fix-desc-'],
            ['file' => '-file-location-', 'method' => '-method-location-'],
            ['missing/call'],
            [['id' => '-p1-', 'snippet' => ['code' => '-pattern-code-', 'first_line' => 42]]],
            [['code' => '-target-snippet-code-', 'first_line_number' => 273]]);

        $metadata = $metadataController->getMetadata('ex1', $detector, '-p-', '-v-', '-m-');

        self::assertEquals([
            'project' => '-p-',
            'version' => '-v-',
            'misuse' => '-m-',
            // REFACTOR merge description and fix description
            'description' => '-desc-',
            'fix_description' => '-fix-desc-',
            'violation_types' => [0 => 'missing/call'],
            'file' => '-file-location-',
            'method' => '-method-location-',
            'diff_url' => '-diff-',
            'snippets' => [0 => ['snippet' => '-target-snippet-code-', 'line' => 273]],
            'patterns' => [0 => ['name' => '-p1-', 'code' => '-pattern-code-','line' => 42]],
            'tags' => []
        ], $metadata);
    }

}
