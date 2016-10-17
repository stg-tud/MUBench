<?php
require_once 'src/sql/query_util.php';

use PHPUnit\Framework\TestCase;

class QueryTest extends TestCase{
    protected $obj; 

    protected function setUp(){
        $this->obj = json_decode('{"findings":[{"a":"1", "b":"2", "c":"3", "d":"4", "e":"5"}]}');
    }

    public function test_build_columns(){
        $columns = build_columns($this->obj->{'findings'});
        $expected = ", id int NOT NULL,a TEXT NOT NULL,b TEXT NOT NULL,c TEXT NOT NULL,d TEXT NOT NULL,e TEXT NOT NULL";
        $this->assertEquals($expected, $columns);
    }

    public function test_insert_statement(){
        $insert = get_insert_statement('table', 'project', 'version', $this->obj->{"findings"}[0]);
        $expected = "INSERT INTO table VALUES ('project','version','1','2','3','4','5');";
        $this->assertEquals($expected, $insert);
    }

    public function test_delete_statement(){
        $delete = get_delete_statement('table', '0');
        $expected = "DELETE FROM table WHERE id=0;";
        $this->assertEquals($expected, $delete);
    }

    public function test_column_query(){
        $query = column_query('table');
        $expected = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='table';";
        $this->assertEquals($expected, $query);
    }
}