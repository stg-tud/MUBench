<?php

class DBConnection {

	private $pdo;
	private $logger;

	function __construct($pdo, $logger){
		$this->logger = $logger;
		$this->pdo = $pdo;
	}

	public function execStatements($statements){
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

	public function deleteMetadata($misuse){
		return "DELETE FROM metadata where misuse='" . $misuse . "';";
	}

	public function insertMetadata($misuse, $desc, $fix_desc, $violation, $file, $method, $code){
		return "INSERT INTO metadata (misuse, description, fix_description, violation_types, file, method, code) VALUES(" . $this->pdo->quote($misuse) . "," . $this->pdo->quote($desc) . "," . $this->pdo->quote($fix_desc) . "," . $this->pdo->quote($violation) . "," . $this->quote($file) . "," . $this->quote($method) . "," . $this->quote($code) . ");";
	}

	public function getStatStatement($table, $project, $version, $result, $runtime, $findings){
		return "INSERT INTO stats (id, result, runtime, number_of_findings) VALUES (" . $this->pdo->quote($table . "_" . $project . "_" . $version) ."," . $this->pdo->quote($result) . "," . $this->pdo->quote($runtime) . "," . $this->pdo->quote($findings) . ");";
	}

	public function getStatDeleteStatement($table, $project, $version){
		return "DELETE FROM stats WHERE id=" . $this->pdo->quote($table . "_" . $project . "_" . $version) .";";
	}

	public function getTableName($ex, $dataset, $detector){
		if(is_null($dataset)){
			return $ex . '_any_' . $detector;
		}
		return $ex . '_' . $dataset . '_' . $detector;
	}

	public function createTableStatement($name, $obj){
		$output = 'CREATE TABLE ' . $name . '(identifier TEXT NOT NULL, project TEXT NOT NULL, version TEXT NOT NULL';
		foreach($obj[0] as $key => $value){
			$output = $output . "," . $key . " TEXT";
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

	public function getStats($id){
		try{
			$query = $this->pdo->query("SELECT result, runtime, number_of_findings FROM stats WHERE id=" . $this->pdo->quote($id) . ";");
		}catch(PDOException $e){
			$this->logger->info("Error: " . $e->getMessage());
		}
		foreach($query as $q){
			return $q;
		}
	}

	public function getSmallDataPotentialHits($table){
		try{
			$query = $this->pdo->query("SELECT project, version, misuse FROM " . $table . ";");
		}catch(PDOException $e){
			$this->logger->info("Error: " . $e->getMessage());
		}
		return $query;
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
		return "DELETE FROM " . $table . " WHERE identifier=" . $this->pdo->quote($project . "." . $version) . ";";
	}

	public function columnQuery($table){
		return "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=" . $this->pdo->quote($table) . ";";
	}
}