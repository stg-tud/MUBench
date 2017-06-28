<?php

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;
use PHPUnit\Framework\TestCase;
use Pixie\QueryBuilder\QueryBuilderHandler;

class DatabaseTestCase extends TestCase
{
    /** @var QueryBuilderHandler pdo */
    protected $pdo;

    /**
     * @var Logger $logger
     */
    protected $logger;

    /**
     * @var DBConnection $db
     */
    protected $db;

    protected $finding_json = <<<EOT
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
                "custom1": "-val1-",
                "custom2": "-val2-"
            }
        ]
    }
EOT;

    protected $metadata_json = <<<EOD
{
    "project": "-p-",
    "version": "-v-",
    "misuse": "-m-",
    "patterns": [
        {
            "snippet": {
                "first_line": 1,
                "code": "-pattern-code-"
            },
            "id": "-p-id-"
        }
    ],
    "violation_types": [
        "superfluous/condition/null_check"
    ],
    "target_snippets": [
        {
            "first_line_number": 273,
            "code": "-code-"
        }
    ],
    "description": "-desc-",
    "location": {
        "file": "-f-",
        "method": "-method-"
    },
    "fix":{
        "diff-url": "-diff-",
        "description": "-fix-desc-"
    }
}
EOD;

    function setUp()
    {
        $connection = new \Pixie\Connection('sqlite', ['driver' => 'sqlite', 'database' => ':memory:']);
        $this->pdo = $connection->getQueryBuilder();
        $mysql_structure = file_get_contents(dirname(__FILE__) . "/../init_db.sql");
        $this->pdo->pdo()->exec($this->mySQLToSQLite($mysql_structure));
        $this->logger = new \Monolog\Logger("test");
        $this->db = new DBConnection($connection, $this->logger);
    }

    private function mySQLToSQLite($mysql){
        $lines = explode("\n", $mysql);
        for ($i = count($lines) - 1; $i >= 0; $i--) {
            // remove all named keys, i.e., leave only PRIMARY keys
            if (strpos($lines[$i], 'KEY `') !== false) {
                $lines[$i] = "";
                $lines[$i - 1] = substr($lines[$i - 1], 0, -1); // remove trailing comma in previous line
            }
        }
        $sqlite = implode("\n", $lines);
        $sqlite = str_replace("AUTO_INCREMENT", "", $sqlite);
        $sqlite = str_replace("int(11)", "INTEGER", $sqlite);
        $sqlite = str_replace(" ENGINE=MyISAM  DEFAULT CHARSET=latin1;", ";", $sqlite);
        echo $sqlite;
        return $sqlite;
    }

}
