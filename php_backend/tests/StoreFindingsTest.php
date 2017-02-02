<?php

require_once "src/ConnectionDB.php";
require_once "src/QueryBuilder.php";
require_once "src/UploadProcessor.php";
require_once "src/DataProcessor.php";
require_once "src/MuBench/Detector.php";

use PHPUnit\Framework\TestCase;

class StoreFindingsTest extends TestCase
{
    function test_store_ex1()
    {
        $pdo = new PDO('sqlite::memory:');
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        $structure_sql = file_get_contents(dirname(__FILE__) . "/../init_db.sql");
        $pdo->exec("CREATE TABLE `detectors` (`id` INTEGER PRIMARY KEY, `name` varchar(100) NOT NULL)");
        $pdo->exec("CREATE TABLE `stats` (`exp` text NOT NULL, `detector` text NOT NULL, `project` text NOT NULL, `version` text NOT NULL, `result` text NOT NULL, `runtime` text NOT NULL, `number_of_findings` text NOT NULL)");
        $pdo->exec("CREATE TABLE `metadata` (`project` text NOT NULL, `version` text NOT NULL, `misuse` text NOT NULL, `description` text NOT NULL, `fix_description` text NOT NULL, `violation_types` text NOT NULL, `file` text NOT NULL, `method` text NOT NULL, `diff_url` text NOT NULL)");
        $pdo->exec("CREATE TABLE `patterns` (`misuse` text NOT NULL, `name` text NOT NULL, `code` text NOT NULL, `line` text NOT NULL)");

        $logger = new \Monolog\Logger("test");
        $db = new DBConnection($pdo, $logger);
        $queryBuilder = new QueryBuilder($pdo, $logger);
        $upload_processor = new UploadProcessor($db, $queryBuilder, $logger);
        $data_processor = new DataProcessor($db, $logger);

        $data = json_decode(<<<EOD
        {
            "detector": "-d-",
            "project": "-p-",
            "version": "-v-",
            "result": "success",
            "runtime": 42.1,
            "number_of_findings": 23,
            "potential_hits": [
                {
                    "misuse": "-m-",
                    "rank": 0,
                    "target_snippets": [
                        {"first_line_number": 5, "code": "-code-"}
                    ],
                    "-custom1-": "-val1-",
                    "-custom2-": "-val2-"
                }
            ]
        }
EOD
        );
        $upload_processor->processData("ex1", $data, $data->{"potential_hits"});
        $detector = $data_processor->getDetector("-d-");
        $runs = $data_processor->getRuns($detector,"ex1");

        $expected_run = [
            "exp" => "ex1",
            "project" => "-p-",
            "version" => "-v-",
            "result" => "success",
            "runtime" => "42.1",
            "number_of_findings" => "23",
            "detector" => "detector_1",
            "misuses" => []
        ];
        self::assertEquals([$expected_run], $runs);
    }

}
