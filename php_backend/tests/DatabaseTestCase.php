<?php
require_once "src/ConnectionDB.php";

use PHPUnit\Framework\TestCase;

class DatabaseTestCase extends TestCase
{

    protected $pdo;
    protected $logger;
    protected $db;

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