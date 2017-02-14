<?php
require_once "src/DBConnection.php";

use PHPUnit\Framework\TestCase;

class DatabaseTestCase extends TestCase
{

    protected $pdo;
    protected $logger;
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
        $this->pdo = new PDO('sqlite::memory:');
        $this->pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        $structure_sql = file_get_contents(dirname(__FILE__) . "/init_sqlite.sql");
        $this->pdo->exec($structure_sql);
        $this->logger = new \Monolog\Logger("test");
        $this->db = new DBConnection($this->pdo, $this->logger);
    }

}