<?php
require_once 'src/QueryBuilder.php';

use PHPUnit\Framework\TestCase;

class ConnectionDBTest extends TestCase
{
    protected $obj;
    protected $db;
    protected $query;
    protected $prefix = 'detector_';

    public function getConnection()
    {
        $pdo = new PDO('sqlite::memory:');
        return $pdo;
    }

    protected function setUp()
    {
        $this->obj = json_decode('{"findings":[{"a":"1", "b":"2", "c":"3", "rank":"4", "misuse":"5"}]}');
        $this->db = new DBConnection($this->getConnection(), new \Monolog\Logger("test"));
        $this->query = new QueryBuilder($this->getConnection(), new \Monolog\Logger("test"));
        $statements[] =
            "CREATE TABLE detectors (id int, name TEXT NOT NULL);";
        $statements[] =
            "INSERT INTO detectors (name, id) VALUES ('MuDetect', 1);";
        $this->db->execStatements($statements);
    }

    public function testgetTableName(){
        $query = $this->db->getTableName('MuDetect');
        $this->assertEquals($this->prefix . "1", $query);
    }

    public function testExecCreateAndInsertTable(){
        $statements = [];
        $tableName = "testTable";
        $statements[] = $this->query->createTableStatement($tableName, $this->obj->{'findings'});
        $statements[] = $this->query->insertStatement($tableName, 'exp', 'project', 'version', $this->obj->{"findings"}[0]);
        $this->db->execStatements($statements);
        $query = $this->db->getPotentialHits($tableName, 'exp', 'project', 'version');
        $this->assertTrue(count($query) != 0);
    }
}