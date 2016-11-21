<?php
require_once 'src/ConnectionDB.php';

use PHPUnit\Framework\TestCase;

class ConnectionDBTest extends TestCase{
    protected $obj; 
    protected $db;

    public function getConnection(){
        $pdo = new PDO('sqlite::memory:');
        return $pdo;
    }

    protected function setUp(){
        $this->obj = json_decode('{"findings":[{"a":"1", "b":"2", "c":"3", "d":"4", "e":"5"}]}');
        $this->db = new DBConnection($this->getConnection(), NULL);
    }

    public function testInsertStatement(){
        $insert = $this->db->insertStatement('table', 'project', 'version', $this->obj->{"findings"}[0]);
        $expected = "INSERT INTO table ( identifier, project, version, a, b, c, d, e) VALUES ('project.version','project','version','1','2','3','4','5');";
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
        $name = $this->db->getTableName('ex1', 'icse15', 'mudetect');
        $expected = 'ex1_icse15_mudetect';
        $this->assertEquals($expected, $name);
    }

    public function testgetTableNameWithNull(){
        $name = $this->db->getTableName('ex1', NULL, 'mudetect');
        $expected = 'ex1_any_mudetect';
        $this->assertEquals($expected, $name);
    }

    public function testColumnStatement(){
        $actual = $this->db->addColumnStatement('table', 'b');
        $expected = 'ALTER TABLE table ADD b TEXT;';
        $this->assertEquals($expected, $actual);
    }

    public function testCreateTableStatement(){
        $actual = $this->db->createTableStatement('table', $this->obj->{'findings'});
        $expected = 'CREATE TABLE table(identifier TEXT NOT NULL, project TEXT NOT NULL, version TEXT NOT NULL,a TEXT,b TEXT,c TEXT,d TEXT,e TEXT);';
        $this->assertEquals($expected, $actual);
    }

    public function testdeleteMetadata(){
        $actual = $this->db->deleteMetadata('misuse');
        $expected = "DELETE FROM metadata WHERE misuse='misuse';";
        $this->assertEquals($expected, $actual);
    }

    public function testInsertMetadata(){
        $actual = $this->db->insertMetadata('misuse', 'desc', 'fix_desc', 'diff_url', 'violation', 'file', 'method');
        $expected = "INSERT INTO metadata (misuse, description, fix_description, diff_url, violation_types, file, method) VALUES('misuse','desc','fix_desc','diff_url','violation','file','method');";        
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
        $actual = $this->db->getStatStatement('table', 'project', 'version', 'result', 'runtime', 'findings', 'table');
        $expected = "INSERT INTO stats (id, result, runtime, number_of_findings, exp, project, version) VALUES ('table_project_version','result','runtime','findings','table','project','version');";
        $this->assertEquals($expected, $actual);
    }

    public function testStatDeleteStatement(){
        $actual = $this->db->getStatDeleteStatement('table', 'project', 'version');
        $expected = "DELETE FROM stats WHERE id='table_project_version';";
        $this->assertEquals($expected, $actual);
    }

}