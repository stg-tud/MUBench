<?php
require_once 'src/util.php';

use PHPUnit\Framework\TestCase;

class UtilTest extends TestCase{
    protected $obj; 

    protected function setUp(){
        $this->obj = json_decode('{"findings":[{"a":"1", "b":"2", "c":"3", "d":"4", "e":"5"}]}');
    }

    public function test_table_name(){
        $name = get_table_name('ex1', 'icse15', 'mudetect');
        $expected = 'ex1_icse15_mudetect';
        $this->assertEquals($expected, $name);
    }

    public function test_validate_columns(){
        $json = $this->obj->{'findings'};
        $table_columns = array('project', 'version', 'a', 'b', 'c', 'd', 'e');
        $this->assertTrue(validate_table_columns($table_columns, $json));
    }

    public function test_json_names(){
        $actual = get_json_names($this->obj->{'findings'});
        $expected = array('project', 'version', 'a', 'b', 'c', 'd', 'e');
        $this->assertEquals($expected, $actual);
    }
}