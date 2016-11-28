<?php

use Monolog\Logger;

class DBConnection {

	private $pdo;
	private $logger;

	function __construct(PDO $pdo, Logger $logger){
		$this->logger = $logger;
		$this->pdo = $pdo;
	}

	public function execStatements($statements){
		foreach($statements as $s){
			try{
	    		$status = $this->pdo->exec($s);
	    		$this->logger->error($status);
			}catch(PDOException $e){
				$this->logger->error("Error execStatement: (" . $e->getMessage() . ") executing " . $s );
			}
		}
	}

	public function getTableColumns($table){
		$sql = $this->columnQuery($table);
	    try{
	    	$query = $this->pdo->query($sql);
		}catch(PDOException $e){
			$this->logger->error("Error getTableColumns: " . $e->getMessage());
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
		return "DELETE FROM metadata WHERE misuse='" . $misuse . "';";
	}

	public function insertMetadata($misuse, $desc, $fix_desc, $diff_url, $violation, $file, $method){
		return "INSERT INTO metadata (misuse, description, fix_description, diff_url, violation_types, file, method) VALUES(" . $this->pdo->quote($misuse) . "," . $this->pdo->quote($desc) . "," . $this->pdo->quote($fix_desc) . "," . $this->pdo->quote($diff_url) . "," . $this->pdo->quote($violation) . "," . $this->pdo->quote($file) . "," . $this->pdo->quote($method) . ");";
	}

	public function insertPattern($misuse, $id, $code, $line){
		return "INSERT INTO patterns (misuse, name, code, line) VALUES(" . $this->pdo->quote($misuse) . "," . $this->pdo->quote($id) . "," . $this->pdo->quote($code) . "," . $this->pdo->quote($line) . ");";
	}

	public function deletePatterns($misuse){
		return "DELETE FROM patterns WHERE misuse='misuse';";
	}

	public function getStatStatement($table, $project, $version, $result, $runtime, $findings){
		return "INSERT INTO stats (id, result, runtime, number_of_findings, exp, project, version) VALUES (" . $this->pdo->quote($table . "_" . $project . "_" . $version) ."," . $this->pdo->quote($result) . "," . $this->pdo->quote($runtime) . "," . $this->pdo->quote($findings) . "," . $this->pdo->quote($table) . "," . $this->pdo->quote($project) . "," . $this->pdo->quote($version) .");";
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
		$values = " VALUES (" . $this->pdo->quote($project . "." . $version) ."," . $this->pdo->quote($project) . "," . $this->pdo->quote($version);
		foreach($obj as $key => $value){
			$output = $output . ", " . $key;
			$values = $values . "," . $this->pdo->quote(is_array($value) ? $this->arrayToString($value) : $value);
		}

		$output = $output . ")";
		$values = $values . ");";
		$output = $output . $values;
		return $output;
	}

	public function arrayToString($json){
		$out = $json[0];
		for($i = 1; $i < count($json); $i++){
			$out = $out . ';' . $json[$i];
		}
		return $out;
	}

	public function getTables(){
		try{
	    	$query = $this->pdo->query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';");
		}catch(PDOException $e){
			$this->logger->error("Error getTables: " . $e->getMessage());
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

	public function getStats($id){
		try{
			$query = $this->pdo->query("SELECT result, runtime, number_of_findings FROM stats WHERE id=" . $this->pdo->quote($id) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getStats: " . $e->getMessage());
		}
		foreach($query as $q){
			return $q;
		}
	}

	public function getAllStats($id){
		try{
			$query = $this->pdo->query("SELECT * FROM stats WHERE exp=" . $this->pdo->quote($id) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getAllStats: " . $e->getMessage());
		}
		$result = [];
		foreach($query as $q){
			$result[] = $q;
		}
		return $result;
	}

	public function getSmallDataPotentialHits($table, $exp){
		$statement = "SELECT project, version, misuse FROM " . $table . ";";
		if($exp === "ex2"){
			$statement = "SELECT project, version, id FROM " . $table . ";";
		}
		try{
			$query = $this->pdo->query($statement);
		}catch(PDOException $e){
			$this->logger->error("Error getSmallDataPotentialHits: " . $e->getMessage());
		}
		return $query;
	}

	public function getMetadata($misuse){
		try{
			$query = $this->pdo->query("SELECT * from metadata WHERE misuse=" . $this->pdo->quote($misuse) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getMetadata: " . $e->getMessage());
		}
		return $query;
	}

	public function getPattern($misuse){
		try{
			$query = $this->pdo->query("SELECT * from patterns WHERE misuse=" . $this->pdo->quote($misuse) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getPattern: " . $e->getMessage());
		}
		return $query;
	}

	public function getReview($user, $identifier){
		try{
			$query = $this->pdo->query("SELECT * from reviews WHERE name=" . $this->pdo->quote($user) . " AND identifier=" . $this->pdo->quote($identifier) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getReview: " . $e->getMessage());
		}
		return $query;
	}

	public function getHits($table, $project, $version, $misuse, $exp){
		try{
			$query = $this->pdo->query("SELECT * from ". $table . " WHERE " . ($exp === "ex2" ? "id=" : "misuse=") . $this->pdo->quote($misuse) . " AND project=" . $this->pdo->quote($project) . " AND version=" . $this->pdo->quote($version) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getHits: " . $e->getMessage());
		}
		return $query;
	}

	public function getPotentialHits($table, $project, $version){
		try{
			$query = $this->pdo->query("SELECT * from ". $table . " WHERE project=" . $this->pdo->quote($project) . " AND version=" . $this->pdo->quote($version) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getPotentialHits: " . $e->getMessage());
		}
		$result = [];
		foreach($query as $q){
			$result[] = $q;
		}
		return $result;
	}

	public function getAllReviews($identifier){
		try{
			$query = $this->pdo->query("SELECT name from reviews WHERE identifier=" . $this->pdo->quote($identifier) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getAllReviews: " . $e->getMessage());
		}
		return $query;
	}

	public function getReviewStatement($identifier, $name, $hit, $comment){
		return "INSERT INTO reviews (identifier, name, hit, comment) VALUES (" . $this->pdo->quote($identifier) . "," . $this->pdo->quote($name) . "," . $this->pdo->quote($hit) . "," . $this->pdo->quote($comment) . ");";
	}

	public function deleteStatement($table, $project, $version){
		return "DELETE FROM " . $table . " WHERE identifier=" . $this->pdo->quote($project . "." . $version) . ";";
	}

	public function columnQuery($table){
		return "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=" . $this->pdo->quote($table) . ";";
	}
}