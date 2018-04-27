<?php

require_once "SlimTestCase.php";

use Illuminate\Support\Facades\Schema;
use MuBench\ReviewSite\Controllers\ImportRunsController;
use MuBench\ReviewSite\Controllers\MetadataController;
use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Controllers\TagsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\Run;
use Illuminate\Container\Container;
use Illuminate\Events\Dispatcher;
use MuBench\ReviewSite\Models\Snippet;
use MuBench\ReviewSite\Models\Violation;

class ImportRunsControllerTest extends SlimTestCase
{
    private $run_with_two_potential_hits_for_one_misuse;
    private $metadata;

    private $db1;

    private $db2;

    function setUp()
    {
        parent::setUp();

        $this->run_with_two_potential_hits_for_one_misuse = [
            "result" => "success",
            "runtime" => 42.1,
            "number_of_findings" => 23,
            "timestamp" => 12,
            "potential_hits" => [
                [
                    "misuse" => "-m-",
                    "rank" => 0,
                    "target_snippets" => [
                        ["first_line_number" => 6, "code" => "-code-"]
                    ],
                    'file' => 'test'
                ],
                [
                    "misuse" => "-m-",
                    "rank" => 2,
                    "target_snippets" => [
                        ["first_line_number" => 5, "code" => "-code-"]
                    ],
                    'file' => 'test'
                ]]
        ];
        $this->metadata = [
            'project' => '-p-',
            'version' => '-v-',
            'misuse' => '-m-',
            'description' => '-desc-',
            'fix' => ['diff-url' => '-diff-', 'description' => '-fix-desc-'],
            'location' => ['file' => '-file-location-', 'method' => '-method-location-'],
            'violations' => ['missing/call'],
            'correct_usages' => [['id' => '-p1-', 'snippet' => ['code' => '-code-', 'first_line' => 42]]],
            'target_snippets' => [['code' => '-target-snippet-code-', 'first_line_number' => 273]]
        ];
        $this->createTempDBFiles();
    }

    function tearDown()
    {
        $this->deleteTempDBFiles();
    }

    function test_import_run()
    {
        // make first db default to fill
        $this->addDBConnections('default', 'extern');
        $this->setupDatabaseTables();

        $this->createFullRunWithReview();
        sleep(1);

        // need to fetch all parts beforehand because relation calls are still made on default connection
        $expectedRun = Run::of(Detector::find('-d-'))->in(Experiment::find(1))->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();
        $expectedRun->setConnection('extern');
        $expectedSnippets = Snippet::all();

        // switch dbs around, extern db is filled
        $this->addDBConnections('extern', 'default');

        $importRunsController = new ImportRunsController($this->container);
        $importRunsController->importRunsFromConnection(1, '-d-', '-p-', '-v-', $this->container['capsule']->getConnection('extern'));

        $importedRun = Run::of(Detector::find('-d-'))->in(Experiment::find(1))->where(['project_muid' => '-p-', 'version_muid' => '-v-'])->first();

        self::assertNotNull($importedRun);
        $expectedRunAttributes = $expectedRun->getAttributes();
        $importedRunAttributes = $importedRun->getAttributes();
        $expectedRunUpdatedAt = $expectedRunAttributes['updated_at'];
        $importedRunUpdatedAt = $importedRunAttributes['updated_at'];

        // remove updated_at from attributes
        unset($expectedRunAttributes['updated_at']);
        unset($importedRunAttributes['updated_at']);

        self::assertEquals($expectedRunAttributes, $importedRunAttributes);
        self::assertNotEquals($expectedRunUpdatedAt, $importedRunUpdatedAt);
        self::assertEquals($expectedRun->misuses, $importedRun->misuses);
        $actualMisuse = $importedRun->misuses[0];
        $expectedMisuse = $expectedRun->misuses[0];
        self::assertNotNull($actualMisuse->metadata);
        self::assertEquals($expectedMisuse->metadata, $actualMisuse->metadata);
        self::assertNotNull($actualMisuse->metadata->violations);
        self::assertEquals($expectedMisuse->metadata->violations, $actualMisuse->metadata->violations);
        self::assertNotNull($actualMisuse->metadata->correct_usages);
        self::assertEquals($expectedMisuse->metadata->correct_usages, $actualMisuse->metadata->correct_usages);
        self::assertNotEmpty($actualMisuse->findings);
        self::assertEquals($expectedMisuse->findings, $actualMisuse->findings);
        self::assertNotEmpty($actualMisuse->snippets());
        self::assertEquals($expectedSnippets, $actualMisuse->snippets());
        self::assertNotEmpty($actualMisuse->misuse_tags);
        self::assertEquals($expectedMisuse->misuse_tags[0]->getAttributes(), $actualMisuse->misuse_tags[0]->getAttributes());
        self::assertNotEmpty($actualMisuse->reviews);
        self::assertEquals($expectedMisuse->reviews, $actualMisuse->reviews);
        $expectedReview = $expectedMisuse->reviews[0];
        $actualReview = $actualMisuse->reviews[0];
        self::assertEquals($expectedReview->reviewer->name, $actualReview->reviewer->name);
        self::assertNotEmpty($actualReview->finding_reviews);
        self::assertEquals($expectedReview->finding_reviews, $actualReview->finding_reviews);
        self::assertEquals($expectedReview->finding_reviews[0]->violations, $actualReview->finding_reviews[0]->violations);
    }

    private function addDBConnections($firstdb, $seconddb)
    {
        /** @var \Slim\Container $container */

        $capsule = new \Illuminate\Database\Capsule\Manager;
        $capsule->addConnection([
            'driver' => 'sqlite',
            'host' => 'localhost',
            'database' => $this->db1,
            'username' => 'admin',
            'password' => 'admin',
            'charset' => 'utf8',
            'collation' => 'utf8_unicode_ci',
            'prefix' => '',
        ], $firstdb);
        $capsule->addConnection([
            'driver' => 'sqlite',
            'host' => 'localhost',
            'database' => $this->db2,
            'username' => 'admin',
            'password' => 'admin',
            'charset' => 'utf8',
            'collation' => 'utf8_unicode_ci',
            'prefix' => '',
        ], $seconddb);
        $capsule->setAsGlobal();
        $capsule->setEventDispatcher(new Dispatcher(new Container()));
        $capsule->bootEloquent();

        $this->container['capsule'] = $capsule;

        // The schema accesses the database through the app, which we do not have in
        // this context. Therefore, use an array to provide the database. This seems
        // to work fine.
        /** @noinspection PhpParamsInspection */

        \Illuminate\Support\Facades\Schema::setFacadeApplication(["db" => $capsule]);
        \MuBench\ReviewSite\Models\Detector::boot();
    }

    private function setupDatabaseTables()
    {
        $schema = Schema::connection('default');
        require __DIR__ . '/../setup/create_database_tables.php';
        $schema = Schema::connection('extern');
        require __DIR__ . '/../setup/create_database_tables.php';
    }

    private function createTempDBFiles()
    {
       $this->db1 = tempnam('./', "test-db-");
       $this->db2 = tempnam('./', "test-db-");
    }

    private function deleteTempDBFiles()
    {
        unlink($this->db1);
        unlink($this->db2);
    }

    public function createFullRunWithReview()
    {
        $runsController = new RunsController($this->container);
        $metadataController = new MetadataController($this->container);
        $tagController = new TagsController($this->container);
        $reviewController = new \MuBench\ReviewSite\Controllers\ReviewsController($this->container);

        $reviewer = Reviewer::create(['name' => 'reviewer']);
        $violation = Violation::create(['name' => 'missing/call']);
        $metadataController->putMetadataCollection([$this->metadata]);
        $runsController->addRun(1, '-d-', '-p-', '-v-', $this->run_with_two_potential_hits_for_one_misuse);
        $tagController->addTagToMisuse(1, 'test-dataset');
        $reviewController->updateOrCreateReview(1, $reviewer->id, '-comment-', [['hit' => 'Yes', 'violations' => [$violation->id]]]);
    }


}
