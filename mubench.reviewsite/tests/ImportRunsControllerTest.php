<?php

require_once "SlimTestCase.php";

use Illuminate\Support\Facades\Schema;
use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Run;
use Illuminate\Container\Container;
use Illuminate\Events\Dispatcher;

class ImportRunsControllerTest extends SlimTestCase
{
    private $run_with_two_potential_hits_for_one_misuse;

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
        $this->createTempDBFiles();
    }

    function tearDown()
    {
        $this->deleteTempDBFiles();
    }

    function test_import_run()
    {
        $this->addDBConnections('default', 'extern');
        $this->setupDatabaseTables();
        $runsController = new RunsController($this->container);
        $runsController->addRun(2, '-d-', '-p-', '-v-', $this->run_with_two_potential_hits_for_one_misuse);
        $expectedRun = Run::of(Detector::find('-d-'))->in(Experiment::find(2))->where(['project' => '-p-', 'version' => '-v-'])->first();

        $this->addDBConnections('extern', 'default');
        $importRunsController = new \MuBench\ReviewSite\Controllers\ImportRunsController($this->container);
        $importRunsController->importRunsFromConnection(2, '-d-', '-p-', '-v-', $this->container['capsule']->getConnection('extern'));
        $importedRun = Run::of(Detector::find('-d-'))->in(Experiment::find(2))->where(['project' => '-p-', 'version' => '-v-'])->first();

        self::assertEquals($expectedRun, $importedRun);
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


}
