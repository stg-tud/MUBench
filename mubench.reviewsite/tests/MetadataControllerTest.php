<?php

namespace MuBench\ReviewSite\Controllers;

require_once "SlimTestCase.php";

use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Metadata;
use MuBench\ReviewSite\Models\Run;
use SlimTestCase;

class MetadataControllerTest extends SlimTestCase
{
    /**
     * @var array
     */
    private $metadata;

    /** @var MetadataController */
    private $metadataController;

    function setUp()
    {
        parent::setUp();
        $this->metadataController = new MetadataController($this->container);
        $this->metadata = [
            'project' => '-p-',
            'version' => '-v-',
            'misuse' => '-m-',
            'description' => '-desc-',
            'fix' => ['diff-url' => '-diff-', 'description' => '-fix-desc-'],
            'location' => ['file' => '-file-location-', 'method' => '-method-location-'],
            'violation_types' => ['missing/call'],
            'patterns' => [['id' => '-p1-', 'snippet' => ['code' => '-pattern-code-', 'first_line' => 42]]],
            'target_snippets' => [['code' => '-target-snippet-code-', 'first_line_number' => 273]]
        ];
    }

    function test_store_metadata()
    {
        $this->metadataController->putMetadataCollection([$this->metadata]);

        $this->metadata = Metadata::where(['project_muid'=> '-p-', 'version_muid' => '-v-', 'misuse_muid' => '-m-'], '=')->first();
        self::assertEquals('-p-', $this->metadata->project_muid);
        self::assertEquals('-v-', $this->metadata->version_muid);
        self::assertEquals('-m-', $this->metadata->misuse_muid);
        self::assertEquals('-desc-', $this->metadata->description);
        self::assertEquals('-fix-desc-', $this->metadata->fix_description);
        self::assertEquals('-file-location-', $this->metadata->file);
        self::assertEquals('-method-location-', $this->metadata->method);
        self::assertEquals('-diff-', $this->metadata->diff_url);
        self::assertEquals(1, count($this->metadata->patterns));
        self::assertEquals('-pattern-code-', $this->metadata->patterns[0]->code);
        self::assertEquals(42, $this->metadata->patterns[0]->line);
        self::assertEquals(1 , count($this->metadata->violation_types()));
        self::assertEquals('missing/call', $this->metadata->violation_types[0]->name);
        // TODO: snippet test if added
    }

    function test_update_metadata()
    {
        $this->metadataController->putMetadataCollection([$this->metadata]);
        $this->metadata['description'] = '-new-desc-';
        $this->metadataController->putMetadataCollection([$this->metadata]);

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

    function test_create_missing_misuses()
    {
        $run_without_hits = [
            "result" => "success",
            "runtime" => 42.1,
            "number_of_findings" => 23,
            "-custom-stat-" => "-stat-val-",
            "timestamp" => 12,
            "potential_hits" => []];
        $detector = Detector::create(['muid' => '-d-']);
        $experiment = Experiment::find(1);
        $runsController = new RunsController($this->container);
        $runsController->addRun($experiment->id, '-d-', '-p-', '-v-',  $run_without_hits);

        $run = Run::of($detector)->in($experiment)->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();
        self::assertEmpty($run->misuses);

        $this->metadataController->putMetadataCollection([$this->metadata]);

        $run = Run::of($detector)->in($experiment)->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();
        self::assertEquals(1, $run->misuses->count());
    }

    function test_update_unlinked_misuses()
    {
        $run_with_potential_hit = [
            "result" => "success",
            "runtime" => 42.1,
            "number_of_findings" => 23,
            "-custom-stat-" => "-stat-val-",
            "timestamp" => 12,
            "potential_hits" => [[
                "misuse" => "-m-",
                "rank" => 0,
                "target_snippets" => [],
                "file" => "//src/file"
            ]]];
        $detector = Detector::create(['muid' => '-d-']);
        $experiment = Experiment::find(1);
        $runsController = new RunsController($this->container);
        $runsController->addRun($experiment->id, '-d-', '-p-', '-v-',  $run_with_potential_hit);

        $run = Run::of($detector)->in($experiment)->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();
        self::assertEquals(1, $run->misuses->count());

        $this->metadataController->putMetadataCollection([$this->metadata]);

        $run = Run::of($detector)->in($experiment)->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();
        self::assertEquals(1, $run->misuses->count());
        self::assertNotNull($run->misuses[0]->metadata_id);
    }
}
