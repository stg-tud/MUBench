<?php

class DBConnection {

	private $pdo;
	private $logger;

	function __construct($pdo, $logger){
		$this->logger = $logger;
		$this->pdo = $pdo;
	}

	public function handleData($ex, $obj, $obj_array){
		$table = $this->getTableName($ex, $obj->{'dataset'}, $obj->{'detector'});
		$project = $obj->{'project'};
		$version = $obj->{'version'};
		$runtime = $obj->{'runtime'};
		$result = $obj->{'result'};
		$findings = $obj->{'number_of_findings'};
		$statements = [];
		$statements[] = $this->getStatDeleteStatement($table, $project, $version);
		$statements[] = $this->getStatStatement($table, $project, $version, $result, $runtime, $findings);
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
	    		//$this->logger->info("Statement: " . $s . " | Changed: " . $status);
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

	public function getStatStatement($table, $project, $version, $result, $runtime, $findings){
		return "INSERT INTO stats (id, result, runtime, number_of_findings) VALUES (" . $this->pdo->quote($table . "_" . $project . "_" . $version) ."," . $this->pdo->quote($result) . "," . $this->pdo->quote($runtime) . "," . $this->pdo->quote($findings) . ");";
	}

	public function getStatDeleteStatement($table, $project, $version){
		return "DELETE FROM stats WHERE id=" . $this->pdo->quote($table . "_" . $project . "_" . $version) .";";
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

	public function getPotentialHits($table){
		try{
			$query = $this->pdo->query("SELECT * FROM " . $table . ";");
		}catch(PDOException $e){
			$this->logger->info("Error: " . $e->getMessage());
		}
		$hits = [];
		$lastIdentifier = "";
		$currentVersion = "";
		$hit = [];
		foreach($query as $q){
			if($lastIdentifier === ""){
				$hit = [];
				$lastIdentifier = $q['project'];
				$hit['project'] = $q['project'];
			}

			if($lastIdentifier === $q['project'] && $currentVersion != $q['version']){
				$hit['versions'][] = $q['version'];
				$currentVersion = $q['version'];
				$hit['stats'][] = $this->getStats($table . "_" . $lastIdentifier . "_" . $currentVersion);
			}
			
			if($lastIdentifier != $q['project'] && $currentVersion != $q['version']){
				$hits[] = $hit;
				$hit = [];
				$hit['project'] = $q['project'];
				$hit['version'][] = $q['version'];
				$lastIdentifier = $q['project'];
				$currentVersion = $q['version'];
			}

			if($lastIdentifier === $q['project'] && $currentVersion === $q['version']){
				$add = true;
				foreach($hit['misuse'][$currentVersion] as $m){
					if($m === $q['misuse']){
						$add = false;
					}
				}
				if($add){
					$hit['misuse'][$currentVersion][] = $q['misuse'];
				}
			}
		}
		$hit['stats'][] = $this->getStats($table . "_" . $lastIdentifier . "_" . $currentVersion);
		$hits[] = $hit;
		return $hits;
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