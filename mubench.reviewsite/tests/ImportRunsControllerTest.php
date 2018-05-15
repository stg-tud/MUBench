<?php

require_once "SlimTestCase.php";

use Illuminate\Database\Eloquent\Model;
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
            'location' => ['file' => '-file-location-', 'method' => '-method-location-', 'line' => -1],
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
        self::assertAttributesEqualExceptUpdatedAt($expectedRun, $importedRun);
        self::assertNotEmpty($importedRun->misuses);
        $actualMisuse = $importedRun->misuses[0];
        $expectedMisuse = $expectedRun->misuses[0];
        self::assertAttributesEqualExceptUpdatedAt($expectedMisuse, $actualMisuse);
        self::assertNotNull($actualMisuse->metadata);
        self::assertAttributesEqualExceptUpdatedAt($expectedMisuse->metadata, $actualMisuse->metadata);
        self::assertNotEmpty($actualMisuse->metadata->violations);
        self::assertEquals($expectedMisuse->metadata->violations[0]->getAttributes(), $actualMisuse->metadata->violations[0]->getAttributes());
        self::assertNotEmpty($actualMisuse->metadata->correct_usages);
        self::assertEquals($expectedMisuse->metadata->correct_usages[0]->getAttributes(), $actualMisuse->metadata->correct_usages[0]->getAttributes());
        self::assertNotEmpty($actualMisuse->findings);
        self::assertAttributesEqualExceptUpdatedAt($expectedMisuse->findings[0], $actualMisuse->findings[0]);
        self::assertNotEmpty($actualMisuse->snippets());
        self::assertEquals($expectedSnippets, $actualMisuse->snippets());
        self::assertNotEmpty($actualMisuse->misuse_tags);
        self::assertEquals($expectedMisuse->misuse_tags[0]->getAttributes(), $actualMisuse->misuse_tags[0]->getAttributes());
        self::assertNotEmpty($actualMisuse->reviews);
        self::assertAttributesEqualExceptUpdatedAt($expectedMisuse->reviews[0], $actualMisuse->reviews[0]);
        $expectedReview = $expectedMisuse->reviews[0];
        $actualReview = $actualMisuse->reviews[0];
        self::assertEquals($expectedReview->reviewer->name, $actualReview->reviewer->name);
        self::assertNotEmpty($actualReview->finding_reviews);
        self::assertEquals($expectedReview->finding_reviews[0]->getAttributes(), $actualReview->finding_reviews[0]->getAttributes());
        self::assertEquals($expectedReview->finding_reviews[0]->violations[0]->getAttributes(), $actualReview->finding_reviews[0]->violations[0]->getAttributes());
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
        foreach(array('default', 'extern') as $connection){
            $schemaSetup = new SchemaSetup($connection);
            $schemaSetup->run();
        }
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

    private function createFullRunWithReview()
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

    private static function assertAttributesEqualExceptUpdatedAt(Model $expectedModel, Model $actualModel){
        $expectedAttributes = $expectedModel->getAttributes();
        $actualAttributes = $actualModel->getAttributes();
        unset($expectedAttributes['updated_at']);
        unset($actualAttributes['updated_at']);
        self::assertEquals($expectedAttributes, $actualAttributes);
        self::assertNotEquals($expectedModel->updated_at, $actualModel->updated_at);
    }


}
