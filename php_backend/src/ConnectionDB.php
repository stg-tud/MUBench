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

	public function handleMetaData($json){
		$deleteStatement = "DELETE FROM metadata where misuse='" . $json->{'misuse'} . "';";
		$this->pdo->exec($deleteStatement);
		$statement = "INSERT INTO metadata (misuse, description, fix_description, violation_types, file, method, code) VALUES( :misuse, :description, :fix_description, :violation_types, :file, :method, :code);";
		$sth = $this->pdo->prepare($statement, array(PDO::ATTR_CURSOR => PDO::CURSOR_FWDONLY));
		$sth->execute(array(':misuse' => $json->{'misuse'}, ':description' => $json->{'description'}, ':fix_description' => $json->{'fix_description'}, ':violation_types' => $this->arrayToString($json->{'violation_types'}), ':file' => $json->{'location'}->{'file'}, ':method' => $json->{'location'}->{'method'}, ':code' => $json->{'code'}));
	}

	public function getData($exp, $detector){
		try{
	    	$query = $this->pdo->query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';");
		}catch(PDOException $e){
			$this->logger->info("Error: " . $e->getMessage());
		}
		$tables = array();
		$results = array();
		if(count($query) == 0){
			return $tables;
		}
		foreach($query as $q){
			$arr = split('[_]', $q[0]);
			if($arr[0] === $exp && $arr[2] === $detector){
				$tables[] = $q[0];
			}
		}
		foreach($tables as $t){
			$statement = "SELECT * FROM " . $t . ";";
			if(count($result) > 0){
				$result = $this->pdo->query($statement);
			}
		}
		return $results;
	}

	public function getMetadata($data){
		try{
	    	$query = $this->pdo->query("SELECT * FROM metadata;");
		}catch(PDOException $e){
			$this->logger->info("Error: " . $e->getMessage());
		} 
		$results = array();
		foreach($query as $q){
			$results[] = $q;
		}
		return $results;
	}

	public function arrayToString($json){
		$out = $json[0] . ';';
		for($i = 1; $i < count($json); $i++){
			$out = $out . ';' . $json[$i];
		}
		return $out;
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



	public function getTables(){
		try{
	    	$query = $this->pdo->query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';");
		}catch(PDOException $e){
			$this->logger->info("Error: " . $e->getMessage());
		}
		$tables = array();
		if(count($query) == 0){
			return $tables;
		}
		foreach($query as $q){
			$tables[] = $q[0];		
		}
		return $tables;
	}

	public function getDatasets($prefix){
		return $this->getPrefixTable($prefix, 1);
	}

	public function getDetectors($prefix){
		return $this->getPrefixTable($prefix, 2);
	}

	public function getPrefixTable($prefix, $suffix){
		$tables = $this->getTables();
		$names = array();
		foreach($tables as $t){
			if(substr($t,0,strlen($prefix)) === $prefix){
				$names[] = split('[_]', $t)[$suffix];
			}
		}
		return $names;
	}

	public function deleteStatement($table, $project, $version){
		return "DELETE FROM " . $table . " WHERE identifier='" . $project . "." . $version . "';";
	}

	public function columnQuery($table){
		return "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='" . $table . "';";
	}
}