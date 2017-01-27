<?php
require_once 'src/ConnectionDB.php';

use PHPUnit\Framework\TestCase;

class ConnectionDBTest extends TestCase{
    protected $obj; 
    protected $db;
    protected $prefix = 'detector_';

    public function getConnection(){
        $pdo = new PDO('sqlite::memory:');
        return $pdo;
    }

    protected function setUp(){
        $this->obj = json_decode('{"findings":[{"a":"1", "b":"2", "c":"3", "rank":"4", "misuse":"5"}]}');
        $this->db = new DBConnection($this->getConnection(), new \Monolog\Logger("test"));
        $statements[] =
            "CREATE TABLE detectors (id int, name TEXT NOT NULL);";
        $statements[] =
            "INSERT INTO detectors (name, id) VALUES ('MuDetect', 1);";
        $this->db->execStatements($statements);
    }

    public function testInsertStatement(){
        $insert = $this->db->insertStatement('table', 'exp', 'project', 'version', $this->obj->{"findings"}[0]);
        $expected = "INSERT INTO table ( exp, project, version, misuse, a, b, c, rank) VALUES ('exp','project','version','5','1','2','3','4');";
        $this->assertEquals($expected, $insert);
    }

    public function testDeleteStatement(){
        $delete = $this->db->deleteStatement('table', 'project', 'version');
        $expected = "DELETE FROM table WHERE identifier='project.version';";
        $this->assertEquals($expected, $delete);
    }

    public function testColumnQuery(){
        $query = $this->db->columnQuery('table');
        $expected = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='table';";
        $this->assertEquals($expected, $query);
    }

    public function testgetTableName(){
        $query = $this->db->getTableName('MuDetect');
        $this->assertEquals($this->prefix . "1", $query);
    }

    public function testColumnStatement(){
        $actual = $this->db->addColumnStatement('table', 'b');
        $expected = 'ALTER TABLE table ADD b TEXT;';
        $this->assertEquals($expected, $actual);
    }

    public function testCreateTableStatement(){
        $actual = $this->db->createTableStatement('table', $this->obj->{'findings'});
        $expected = 'CREATE TABLE table(exp VARCHAR(100) NOT NULL, project VARCHAR(100) NOT NULL, version VARCHAR(100) NOT NULL, misuse VARCHAR(100) NOT NULL,a TEXT,b TEXT,c TEXT,rank VARCHAR(100), PRIMARY KEY(exp, project, version, misuse, rank));';
        $this->assertEquals($expected, $actual);
    }

    public function testdeleteMetadata(){
        $actual = $this->db->deleteMetadata('misuse');
        $expected = "DELETE FROM metadata WHERE misuse='misuse';";
        $this->assertEquals($expected, $actual);
    }

    public function testInsertMetadata(){
        $actual = $this->db->insertMetadata('project', 'version', 'misuse', 'desc', 'fix_desc', 'diff_url', 'violation', 'file', 'method');
        $expected = "INSERT INTO metadata (project, version, misuse, description, fix_description, diff_url, violation_types, file, method) VALUES('project','version','misuse','desc','fix_desc','diff_url','violation','file','method');";
        $this->assertEquals($expected, $actual);
    }

    public function testInsertPattern(){
        $actual = $this->db->insertPattern('misuse', 'id', 'code', 'line');
        $expected = "INSERT INTO patterns (misuse, name, code, line) VALUES('misuse','id','code','line');";
        $this->assertEquals($expected, $actual);
    }

    public function testDeletePatterns(){
        $actual = $this->db->deletePatterns('misuse');
        $expected = "DELETE FROM patterns WHERE misuse='misuse';";
        $this->assertEquals($expected, $actual);
    }

    public function testGetStatsStateent(){
        $actual = $this->db->getStatStatement('table', 'project', 'version', 'result', 'runtime', 'findings', 'exp');
        $expected = "INSERT INTO stats (id, result, runtime, number_of_findings, table_id, exp, project, version) VALUES ('table_project_version','result','runtime','findings','table','exp','project','version');";
        $this->assertEquals($expected, $actual);
    }

    public function testStatDeleteStatement(){
        $actual = $this->db->getStatDeleteStatement('table', 'project', 'version');
        $expected = "DELETE FROM stats WHERE id='table_project_version';";
        $this->assertEquals($expected, $actual);
    }

    public function testDeleteReviewStatement(){
        $actual = $this->db->getReviewDeleteStatement("ex1", "detect1", "proc1", "vers1", "misuse1", "test");
        $expected = "DELETE FROM reviews WHERE exp='ex1' AND detector='detect1' AND project='proc1' AND version='vers1' AND misuse='misuse1' AND name='test';";
        $this->assertEquals($expected, $actual);
    }

    public function testInsertReviewStatement(){
        $actual = $this->db->getReviewStatement("ex1", "detect1", "proc1", "vers1", "misuse1", "test", "test-comment");
        $expected = "INSERT INTO reviews (exp, detector, project, version, misuse, name, comment) VALUES ('ex1','detect1','proc1','vers1','misuse1','test','test-comment');";
        $this->assertEquals($expected, $actual);
    }

    public function testExecCreateAndInsertTable(){
        $statements = [];
        $tableName = "testTable";
        $statements[] = $this->db->createTableStatement($tableName, $this->obj->{'findings'});
        $statements[] = $this->db->insertStatement($tableName, 'exp', 'project', 'version', $this->obj->{"findings"}[0]);
        $this->db->execStatements($statements);
        $query = $this->db->getPotentialHits($tableName, 'exp', 'project', 'version');
        $this->assertTrue(count($query) != 0);
    }

}