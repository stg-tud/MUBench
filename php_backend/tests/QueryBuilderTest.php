<?php
require_once 'src/QueryBuilder.php';

use PHPUnit\Framework\TestCase;

class QueryBuilderTest extends TestCase
{
    protected $obj;
    protected $queryBuilder;
    protected $prefix = 'detector_';

    public function getConnection()
    {
        $pdo = new PDO('sqlite::memory:');
        return $pdo;
    }

    protected function setUp()
    {
        $this->obj = json_decode('{"findings":[{"a":"1", "b":"2", "c":"3", "rank":"4", "misuse":"5"}]}');
        $this->queryBuilder = new QueryBuilder($this->getConnection(), new \Monolog\Logger("test"));
    }

    public function testInsertStatement()
    {
        $insert = $this->queryBuilder->insertStatement('table', 'exp', 'project', 'version', $this->obj->{"findings"}[0]);
        $expected = "INSERT INTO table ( exp, project, version, misuse, a, b, c, rank) VALUES ('exp','project','version','5','1','2','3','4');";
        $this->assertEquals($expected, $insert);
    }

    public function testDeleteStatement()
    {
        $delete = $this->queryBuilder->deleteStatement('table', 'project', 'version');
        $expected = "DELETE FROM table WHERE identifier='project.version';";
        $this->assertEquals($expected, $delete);
    }

    public function testColumnQuery()
    {
        $query = $this->queryBuilder->columnQuery('table');
        $expected = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='table';";
        $this->assertEquals($expected, $query);
    }

    public function testColumnStatement()
    {
        $actual = $this->queryBuilder->addColumnStatement('table', 'b');
        $expected = 'ALTER TABLE table ADD b TEXT;';
        $this->assertEquals($expected, $actual);
    }

    public function testCreateTableStatement()
    {
        $actual = $this->queryBuilder->createTableStatement('table', $this->obj->{'findings'});
        $expected = 'CREATE TABLE table(exp VARCHAR(100) NOT NULL, project VARCHAR(100) NOT NULL, version VARCHAR(100) NOT NULL, misuse VARCHAR(100) NOT NULL,a TEXT,b TEXT,c TEXT,rank VARCHAR(100), PRIMARY KEY(exp, project, version, misuse, rank));';
        $this->assertEquals($expected, $actual);
    }

    public function testdeleteMetadata()
    {
        $actual = $this->queryBuilder->deleteMetadata('misuse');
        $expected = "DELETE FROM metadata WHERE misuse='misuse';";
        $this->assertEquals($expected, $actual);
    }

    public function testInsertMetadata()
    {
        $actual = $this->queryBuilder->insertMetadata('project', 'version', 'misuse', 'desc', 'fix_desc', 'diff_url', 'violation', 'file', 'method');
        $expected = "INSERT INTO metadata (project, version, misuse, description, fix_description, diff_url, violation_types, file, method) VALUES('project','version','misuse','desc','fix_desc','diff_url','violation','file','method');";
        $this->assertEquals($expected, $actual);
    }

    public function testInsertPattern()
    {
        $actual = $this->queryBuilder->insertPattern('misuse', 'id', 'code', 'line');
        $expected = "INSERT INTO patterns (misuse, name, code, line) VALUES('misuse','id','code','line');";
        $this->assertEquals($expected, $actual);
    }

    public function testDeletePatterns()
    {
        $actual = $this->queryBuilder->deletePatterns('misuse');
        $expected = "DELETE FROM patterns WHERE misuse='misuse';";
        $this->assertEquals($expected, $actual);
    }

    public function testGetStatsStateent()
    {
        $actual = $this->queryBuilder->getStatStatement('table', 'project', 'version', 'result', 'runtime', 'findings', 'exp');
        $expected = "INSERT INTO stats (exp, detector, project, version, result, runtime, number_of_findings) VALUES ('exp','table','project','version','result','runtime','findings');";
        $this->assertEquals($expected, $actual);
    }

    public function testStatDeleteStatement()
    {
        $actual = $this->queryBuilder->getStatDeleteStatement('exp', 'table', 'project', 'version');
        $expected = "DELETE FROM stats WHERE exp='exp' AND detector='table' AND project='project' AND version='version';";
        $this->assertEquals($expected, $actual);
    }

    public function testDeleteReviewStatement()
    {
        $actual = $this->queryBuilder->getReviewDeleteStatement("ex1", "detect1", "proc1", "vers1", "misuse1", "test");
        $expected = "DELETE FROM reviews WHERE exp='ex1' AND detector='detect1' AND project='proc1' AND version='vers1' AND misuse='misuse1' AND name='test';";
        $this->assertEquals($expected, $actual);
    }

    public function testInsertReviewStatement()
    {
        $actual = $this->queryBuilder->getReviewStatement("ex1", "detect1", "proc1", "vers1", "misuse1", "test", "test-comment");
        $expected = "INSERT INTO reviews (exp, detector, project, version, misuse, name, comment) VALUES ('ex1','detect1','proc1','vers1','misuse1','test','test-comment');";
        $this->assertEquals($expected, $actual);
    }

    public function testInsertFindingSnippet()
    {
        $actual = $this->queryBuilder->getFindingSnippetStatement("d", "p1", "v1", "1", "code", "1");
        $expected = "INSERT INTO finding_snippets (detector, project, version, finding, snippet, line) VALUES('d','p1','v1','1','code','1');";
        $this->assertEquals($expected, $actual);
    }

}