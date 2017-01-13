<?php
require_once 'src/ConnectionDB.php';
require_once 'src/UploadProcessor.php';

use PHPUnit\Framework\TestCase;

class DataProcessorTest extends TestCase
{
    protected $obj;
    protected $data;
    protected $db;


    public function getConnection()
    {
        $pdo = new PDO('sqlite::memory:');
        return $pdo;
    }

    protected function setUp()
    {
        $this->db = new DBConnection($this->getConnection(), new \Monolog\Logger("test"));
        $statements = [];
        $statements[] =
            "CREATE TABLE stats (id TEXT NOT NULL, result TEXT NOT NULL, runtime TEXT NOT NULL, number_of_findings TEXT NOT NULL, exp TEXT NOT NULL, project TEXT NOT NULL, version TEXT NOT NULL);";
        $statements[] =
            "CREATE TABLE metadata (misuse TEXT NOT NULL,description TEXT NOT NULL,fix_description TEXT NOT NULL,violation_types TEXT NOT NULL,file TEXT NOT NULL,method TEXT NOT NULL,diff_url TEXT NOT NULL);";
        $statements[] =
            "CREATE TABLE patterns (misuse TEXT NOT NULL,name TEXT NOT NULL,code TEXT NOT NULL,line TEXT NOT NULL);";
        $statements[] =
            "CREATE TABLE reviews (identifier TEXT NOT NULL,name TEXT NOT NULL,hit TEXT NOT NULL,comment TEXT NOT NULL,violation_type TEXT NOT NULL,id TEXT NOT NULL);";
        $this->db->execStatements($statements);
        $this->obj =
            json_decode('{"findings":[{"target_snippets":[{"first_line_number":0, "code":"c"}],"a":"1", "b":"2", "c":"3", "d":"4", "e":"5"}], "project":"p", "version":"v", "runtime":"0", "result":"success", "number_of_findings":"1", "dataset":"any", "detector":"mudetect"}');
        $this->metaObj =
            json_decode('{"misuse":"m.1", "fix":{"diff-url":"url", "description":"desc"}, "description":"d", "violation_types":["1","2"], "location":{"file":"f", "method":"m"}, "patterns":[{"id":"1","snippet":{"code":"c", "first_line":0}}]}');
        $this->reviewObj = array("review_name" => "admin", "review_identifier" => "id", "review_comment" => "test",
            "review_hit" => array(0 => array("hit" => "Yes", "types" => ["1", "2"])));
        $this->data = new DataProcessor($this->db,
            new \Monolog\Logger("test"));
    }

    public function testGetTodo(){
        // TODO implement this
    }
}