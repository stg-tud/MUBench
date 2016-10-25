<?php

class DBConnection {

	private $pdo;
	private $logger;

	function __construct(){

	}

	public function connectDB($server, $dbname, $username, $password, $logger){
		$this->pdo = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
		$this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION, PDO::MYSQL_ATTR_USE_BUFFERED_QUERY);
		$this->logger = $logger;
		$this->logger->info("Database connnected");
	}

	public function handleData($ex, $obj, $obj_array){
		$table = $this->getTableName($ex, $obj->{'dataset'}, $obj->{'detector_name'});
		$project = $obj->{'project'};
		$version = $obj->{'version'};
		$statements = [];
		$columns = $this->getTableColumns($table);
		$obj_columns = $this->getJsonNames($obj_array);
		if(count($columns) == 0){
			$statements[] = $this->createTableStatement($table, $obj_array);
		}
		$statements[] = $this->deleteStatement($table, $project, $version);
		$columns = $this->getTableColumns($table);
		foreach($obj_columns as $c){
			$add = true;
			foreach($columns as $oc){
				if($c == $oc){
					$add = false;
					break;
				}
			}
			if($add){
				$statements[] = $this->addColumnStatement($table, $c);
			}
		}
		foreach($obj_array as $hit){
			$statements[] = $this->insertStatement($table, $project, $version, $hit);
			
		}
		$this->execStatements($statements);
	}

	private function execStatements($statements){
		foreach($statements as $s){
			try{
	    		$status = $this->pdo->exec($s);
	    		$this->logger->info("Statement: " . $s . " | Changed: " . $status);
			}catch(PDOException $e){
				$this->logger->info("Error: " . $e->getMessage());
			}
		}
	}

	public function getTableColumns($table){
		$sql = $this->columnQuery($table);
	    try{
	    	$query = $this->pdo->query($sql);
		}catch(PDOException $e){
			$this->logger->info("Error: " . $e->getMessage());
		}
		$columns = array();
		if(count($query) == 0){
			return $columns;
		}
		foreach($query as $q){
			$columns[] = $q[0];
		}
		return $columns;
	}

	public function getJsonNames($obj){
		$columns = array();
		$columns[] = 'project';
		$columns[] = 'version';
		foreach($obj[0] as $key => $value){
			$columns[] = $key;
		}
		return $columns;
	}

	public function getTableName($ex, $dataset, $detector){
		return $ex . '_' . $dataset . '_' . $detector;
	}

	public function createTableStatement($name, $obj){
		$output = 'CREATE TABLE ' . $name . '(identifier TEXT NOT NULL, project TEXT NOT NULL, version TEXT NOT NULL, id TEXT NOT NULL';
		foreach($obj[0] as $key => $value){
			if($value != "id"){
				$output = $output . "," . $key . " TEXT";
			}
		}
		$output = $output . ');';
		return $output;
	}

	public function addColumnStatement($table, $column){
		return 'ALTER TABLE ' . $table . ' ADD ' . $column . ' TEXT;';
	}

	public function insertStatement($table, $project, $version, $obj){
		$output = "INSERT INTO " . $table . " ( identifier, project, version";
		$values = " VALUES ('" . $project . "." . $version ."','" . $project . "','" . $version;
		foreach($obj as $key => $value){
			$output = $output . ", " . $key;
			$values = $values . "','" . $value;
		}

		$output = $output . ")";
		$values = $values . "');";
		$output = $output . $values;
		return $output;
	}

	public function deleteStatement($table, $project, $version){
		return "DELETE FROM " . $table . " WHERE identifier='" . $project . "." . $version . "';";
	}

	public function columnQuery($table){
		return "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='" . $table . "';";
	}
}