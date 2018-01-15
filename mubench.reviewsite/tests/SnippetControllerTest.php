<?php

use MuBench\ReviewSite\Controllers\SnippetsController;
use MuBench\ReviewSite\Models\Snippet;

require_once 'SlimTestCase.php';

class SnippetControllerTest extends SlimTestCase
{
    /** @var SnippetsController */
    private $snippetController;


    function setUp()
    {
        parent::setUp();
        $this->snippetController = new SnippetsController($this->container);
    }

    function test_snippet_creation()
    {
        $this->snippetController->createSnippetIfNotExists('-p-', '-v-', '-m-', '//src/file', 10, '-code-');
        $actualSnippets = Snippet::of('-p-', '-v-', '-m-', '//src/file')->get();
        self::assertEquals(1, $actualSnippets->count());
        $actualSnippet = $actualSnippets->first();
        self::assertEquals('-p-', $actualSnippet->project_muid);
        self::assertEquals('-v-', $actualSnippet->version_muid);
        self::assertEquals('-m-', $actualSnippet->misuse_muid);
        self::assertEquals('-code-', $actualSnippet->snippet);
        self::assertEquals(10, $actualSnippet->line);
    }

    function test_no_duplicates()
    {
        $this->snippetController->createSnippetIfNotExists('-p-', '-v-', '-m-', '//src/file', 10, '-code-');
        $this->snippetController->createSnippetIfNotExists('-p-', '-v-', '-m-', '//src/file', 10, '-code-');
        self::assertEquals(1, Snippet::all()->count());
    }
}
