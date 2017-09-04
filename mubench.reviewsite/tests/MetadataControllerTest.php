<?php

namespace MuBench\ReviewSite\Controllers;

require_once "SlimTestCase.php";

use MuBench\ReviewSite\Models\Metadata;
use SlimTestCase;

class MetadataControllerTest extends SlimTestCase
{
    /** @var MetadataController */
    private $metadataController;

    function setUp()
    {
        parent::setUp();
        $this->metadataController = new MetadataController($this->container);
    }

    function test_store_metadata()
    {
        $this->metadataController->updateMetadata('-p-', '-v-', '-m-', '-desc-',
            ['diff-url' => '-diff-', 'description' => '-fix-desc-'],
            ['file' => '-file-location-', 'method' => '-method-location-'],
            ['missing/call'],
            [['id' => '-p1-', 'snippet' => ['code' => '-pattern-code-', 'first_line' => 42]]],
            [['code' => '-target-snippet-code-', 'first_line_number' => 273]]);


        $metadata = Metadata::where(['project_muid'=> '-p-', 'version_muid' => '-v-', 'misuse_muid' => '-m-'], '=')->first();
        self::assertEquals('-p-', $metadata->project_muid);
        self::assertEquals('-v-', $metadata->version_muid);
        self::assertEquals('-m-', $metadata->misuse_muid);
        self::assertEquals('-desc-', $metadata->description);
        self::assertEquals('-fix-desc-', $metadata->fix_description);
        self::assertEquals('-file-location-', $metadata->file);
        self::assertEquals('-method-location-', $metadata->method);
        self::assertEquals('-diff-', $metadata->diff_url);
        self::assertEquals(1, count($metadata->patterns));
        self::assertEquals('-pattern-code-', $metadata->patterns[0]->code);
        self::assertEquals(42, $metadata->patterns[0]->line);
        self::assertEquals(1 , count($metadata->violation_types()));
        self::assertEquals('missing/call', $metadata->violation_types[0]->name);
        // TODO: snippet test if added
    }

    function test_update_metadata()
    {
        // new description passed, everything else as in the first test
        $this->metadataController->updateMetadata('-p-', '-v-', '-m-', '-new-desc-',
            ['diff-url' => '-diff-', 'description' => '-fix-desc-'],
            ['file' => '-file-location-', 'method' => '-method-location-'],
            ['missing/call'],
            [['id' => '-p1-', 'snippet' => ['code' => '-pattern-code-', 'first_line' => 42]]],
            [['code' => '-target-snippet-code-', 'first_line_number' => 273]]);

        $metadata = Metadata::where('project_muid', '-p-')->where('version_muid', '-v-')->where('misuse_muid', '-m-')->first();

        self::assertEquals(1, $metadata->id);
        self::assertEquals('-p-', $metadata->project_muid);
        self::assertEquals('-v-', $metadata->version_muid);
        self::assertEquals('-m-', $metadata->misuse_muid);
        self::assertEquals('-new-desc-', $metadata->description);
        self::assertEquals('-fix-desc-', $metadata->fix_description);
        self::assertEquals('-file-location-', $metadata->file);
        self::assertEquals('-method-location-', $metadata->method);
        self::assertEquals('-diff-', $metadata->diff_url);
        self::assertEquals(1, count($metadata->patterns));
        self::assertEquals('-pattern-code-', $metadata->patterns[0]->code);
        self::assertEquals(42, $metadata->patterns[0]->line);
        self::assertEquals(1 , count($metadata->violation_types()));
        self::assertEquals('missing/call', $metadata->violation_types[0]->name);
        // TODO: snippet test if added
    }

}
