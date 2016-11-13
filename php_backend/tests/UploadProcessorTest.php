<?php
require_once 'src/ConnectionDB.php';
require_once 'src/UploadProcessor.php';

use PHPUnit\Framework\TestCase;

class UploadProcessorTest extends TestCase{
    protected $obj; 
    protected $proc;

    public function getConnection(){
        $pdo = new PDO('sqlite::memory:');
        return $pdo;
    }

    protected function setUp(){
        $this->obj = json_decode('{"findings":[{"a":"1", "b":"2", "c":"3", "d":"4", "e":"5"}]}');
        $this->proc = new UploadProcessor(new DBConnection($this->getConnection(), NULL));
    }

    public function testgetJsonNames(){
        $actual = $this->proc->getJsonNames($this->obj->{'findings'});
        $expected = array('project', 'version', 'a', 'b', 'c', 'd', 'e');
        $this->assertEquals($expected, $actual);
    }

    public function testarrayToString(){
        $actual = $this->proc->arrayToString(json_decode('{"violation_type":["first", "second"]}')->{'violation_type'});
        $expected = "first;second";
        $this->assertEquals($expected, $actual);
    }
}