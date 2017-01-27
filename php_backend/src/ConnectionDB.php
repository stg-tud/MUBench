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
			$this->execStatement($s);
		}
	}

    public function execStatement($statement){
        try{
            $status = $this->pdo->exec($statement);
            $this->logger->info("Status execStatement: " . $status . " executing . " . substr($statement, 0, 10));
        }catch(PDOException $e){
            $this->logger->error("Error execStatement: (" . $e->getMessage() . ") executing " . $statement );
        }
    }

	public function getTableColumns($table){
		$sql = $this->columnQuery($table);
		$query = [];
	    try{
	    	$query = $this->pdo->query($sql);
		}catch(PDOException $e){
			$this->logger->error("Error getTableColumns: " . $e->getMessage());
		}
		$columns = array();
		if(!$query){
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

	public function insertMetadata($project, $version, $misuse, $desc, $fix_desc, $diff_url, $violation, $file, $method){
		return "INSERT INTO metadata (project, version, misuse, description, fix_description, diff_url, violation_types, file, method) VALUES(" . $this->pdo->quote($project) . "," . $this->pdo->quote($version) . "," . $this->pdo->quote($misuse) . "," . $this->pdo->quote($desc) . "," . $this->pdo->quote($fix_desc) . "," . $this->pdo->quote($diff_url) . "," . $this->pdo->quote($violation) . "," . $this->pdo->quote($file) . "," . $this->pdo->quote($method) . ");";
	}

	public function insertPattern($misuse, $id, $code, $line){
		return "INSERT INTO patterns (misuse, name, code, line) VALUES(" . $this->pdo->quote($misuse) . "," . $this->pdo->quote($id) . "," . $this->pdo->quote($code) . "," . $this->pdo->quote($line) . ");";
	}

	public function deletePatterns($misuse){
		return "DELETE FROM patterns WHERE misuse='misuse';";
	}

	public function getStatStatement($table, $project, $version, $result, $runtime, $findings, $exp){
		return "INSERT INTO stats (id, result, runtime, number_of_findings, table_id, exp, project, version) VALUES (" . $this->pdo->quote($table . "_" . $project . "_" . $version) ."," . $this->pdo->quote($result) . "," . $this->pdo->quote($runtime) . "," . $this->pdo->quote($findings) . "," . $this->pdo->quote($table) . "," . $this->pdo->quote($exp) . ",". $this->pdo->quote($project) . "," . $this->pdo->quote($version) .");";
	}

	public function getStatDeleteStatement($table, $project, $version){
		return "DELETE FROM stats WHERE id=" . $this->pdo->quote($table . "_" . $project . "_" . $version) .";";
	}

	public function getTableName($detector){
	    $query = [];
	    $sql = "SELECT id from detectors WHERE name=" . $this->pdo->quote($detector) .";";
	    try{
	        $query = $this->pdo->query($sql);
        }catch(PDOException $e){
	        $this->logger->error("Error getTableName: " . $e->getMessage());
        }
        $columns = array();
        if(!$query){
            return NULL;
        }
        foreach($query as $q){
            $columns[] = $q[0];
        }
        if(empty($columns)){
            $sql = "INSERT INTO detectors (name) VALUES(" . $this->pdo->quote($detector) . ");";
            try{
                $this->pdo->exec($sql);
            }catch(PDOException $e){
                $this->logger->error("Error getTableName creating new entry: " . $e->getMessage());
            }
            return $this->getTableName($detector);
        }else{
            return "detector_" . $columns[0];
        }
	}

	public function createTableStatement($name, $obj){
	    // exp project version misuse rank (AUTO INCREMENT id)
		$output = 'CREATE TABLE ' . $name . '(exp VARCHAR(100) NOT NULL, project VARCHAR(100) NOT NULL, version VARCHAR(100) NOT NULL, misuse VARCHAR(100) NOT NULL';
		foreach($obj[0] as $key => $value){
		    if($key === "id" || $key === "misuse") {
            }else if($key === "rank"){
                $output = $output . "," . $key . " VARCHAR(100)";
            }else {
                $output = $output . "," . $key . " TEXT";
            }
		}
		$output = $output . ', PRIMARY KEY(exp, project, version, misuse, rank));';
		return $output;
	}

	public function getAllReviews(){
        $query = [];
        try{
            $query = $this->pdo->query("SELECT * from reviews;");
        }catch(PDOException $e){
            $this->logger->error("Error getAllReview: " . $e->getMessage());
        }
        return $query;
    }

	public function addColumnStatement($table, $column){
		return 'ALTER TABLE ' . $table . ' ADD ' . $column . ' TEXT;';
	}

	public function insertStatement($table, $exp, $project, $version, $obj){
		$output = "INSERT INTO " . $table . " ( exp, project, version, misuse";
		$values = " VALUES (" . $this->pdo->quote($exp) . "," . $this->pdo->quote($project) . "," . $this->pdo->quote($version) . "," . $this->pdo->quote($exp !== "ex2" ? $obj->{'misuse'} : $obj->{'rank'});
		foreach($obj as $key => $value){
            if($key === "id" || $key === "misuse"){
            }else {
                $output = $output . ", " . $key;
                $values = $values . "," . $this->pdo->quote(is_array($value) ? $this->arrayToString($value) : $value);
            }
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

	public function getDetectorTable($detector){
        $query = [];
        try{
            $query = $this->pdo->query("SELECT id FROM detectors WHERE name=" . $this->pdo->quote($detector) . ";");
        }catch(PDOException $e){
            $this->logger->error("Error getDetectorTable: " . $e->getMessage());
        }
        foreach($query as $q){
            return "detector_" . $q[0];
        }

    }

	public function hasFindingForExp($exp, $detector){
        $query = [];
        try{
            $query = $this->pdo->query("SELECT * FROM " . $detector . " WHERE exp=" . $this->pdo->quote($exp) . " LIMIT 1;");
        }catch(PDOException $e){
            $this->logger->error("Error findingForExp: " . $e->getMessage());
        }
        $tables = [];
        foreach($query as $q){
            $tables[] = $q[0];
        }
        return !empty($tables);
    }

	public function getDetectorsTables(){
	    $query = [];
		try{
	    	$query = $this->pdo->query("SELECT * FROM  detectors;");
		}catch(PDOException $e){
			$this->logger->error("Error getTables: " . $e->getMessage());
		}
		$tables = array();
		if(count($query) == 0){
			return $tables;
		}
		foreach($query as $q){
		    $detector = [];
		    $detector['name'] = $q['name'];
		    $detector['id'] = "detector_" . $q['id'];
			$tables[] = $detector;

		}
		return $tables;
	}

	public function hasStats($detector_table, $exp){
	    $query = [];
	    try{
	        $query = $this->pdo->query("SELECT * FROM stats WHERE table_id=" . $this->pdo->quote($detector_table) . " AND exp=". $this->pdo->quote($exp) . ";");
        }catch(PDOException $e){
            $this->logger->error("Error hasStats: " . $e->getMessage());
        }
        $result = $this->queryToArray($query);
        return count($result) > 0;
    }

	public function getStats($id){
        $query = [];
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
        $query = [];
		try{
			$query = $this->pdo->query("SELECT * FROM stats WHERE table_id=" . $this->pdo->quote($id) . ";");
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
        $query = [];
		try{
			$query = $this->pdo->query($statement);
		}catch(PDOException $e){
			$this->logger->error("Error getSmallDataPotentialHits: " . $e->getMessage());
		}
		return $query;
	}

	public function getMetadata($project, $version, $misuse){
        $query = [];
		try{
			$query = $this->pdo->query("SELECT * from metadata WHERE project=" . $this->pdo->quote($project) . " AND version=" . $this->pdo->quote($version) . " AND misuse=" . $this->pdo->quote($misuse) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getMetadata: " . $e->getMessage());
		}
		return $query;
	}

	public function getPattern($misuse){
	    $query = [];
		try{
			$query = $this->pdo->query("SELECT * from patterns WHERE misuse=" . $this->pdo->quote($misuse) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getPattern: " . $e->getMessage());
		}
		return $query;
	}

	public function getReview($exp, $detector, $project, $version, $misuse, $name){
        $query = [];
		try{
		    $query = $this->pdo->query("SELECT * from reviews WHERE name=" . $this->pdo->quote($name) . " AND exp=" . $this->pdo->quote($exp) . " AND detector=" . $this->pdo->quote($detector) . " AND project=" . $this->pdo->quote($project) . " AND version=" . $this->pdo->quote($version) . " AND misuse=" . $this->pdo->quote($misuse) .";");
		}catch(PDOException $e){
			$this->logger->error("Error getReview: " . $e->getMessage());
		}
        if(!$query){
            return [];
        }
        foreach($query as $q){
            return  $q;
        }
	}

	public function getHits($table, $project, $version, $misuse, $exp){
        $query = [];
		try{
			$query = $this->pdo->query("SELECT * from ". $table . " WHERE exp=" . $this->pdo->quote($exp) ." AND misuse=". $this->pdo->quote($misuse) . " AND project=" . $this->pdo->quote($project) . " AND version=" . $this->pdo->quote($version) . " ORDER BY `rank` * 1 ASC;");
		}catch(PDOException $e){
			$this->logger->error("Error getHits: " . $e->getMessage());
		}
		return $query;
	}

	public function getMisusesFromMeta($project, $version){
	    $query = [];
	    try{
	        $query = $this->pdo->query("SELECT * FROM metadata WHERE project=". $this->pdo->quote($project) . " AND version=" . $this->pdo->quote($version) . ";");
        }catch(PDOException $e){
	        $this->logger->error("Error getMisusesFromMeta: " . $e->getMessage());
        }
        return $query;
    }

	public function getPotentialHits($table, $exp, $project, $version){
        $query = [];
		try{
			$query = $this->pdo->query("SELECT * from ". $table . " WHERE exp=". $this->pdo->quote($exp) . " AND project=" . $this->pdo->quote($project) . " AND version=" . $this->pdo->quote($version) . ";");
		}catch(PDOException $e){
			$this->logger->error("Error getPotentialHits: " . $e->getMessage());
		}
		if(!$query){
		    return [];
        }
		$result = [];
		foreach($query as $q){
			$result[] = $q;
		}
		return $result;
	}

	public function getReviewsByIdentifier($exp, $detector, $project, $version, $misuse){
        $query = [];
		try{
			$query = $this->pdo->query("SELECT name from reviews WHERE exp=" . $this->pdo->quote($exp) . " AND detector=" . $this->pdo->quote($detector) . " AND project=" . $this->pdo->quote($project) . " AND version=" . $this->pdo->quote($version) . " AND misuse=" . $this->pdo->quote($misuse) . " ORDER BY `name`;");
		}catch(PDOException $e){
			$this->logger->error("Error getAllReviews: " . $e->getMessage());
		}
		return $query;
	}

	public function getReviewsByReviewer($reviewer){
        $query = [];
        try{
            $query = $this->pdo->query("SELECT * from reviews WHERE name=" . $this->pdo->quote($reviewer) . ";");
        }catch(PDOException $e){
            $this->logger->error("Error getReviewsByReviewer: " . $e->getMessage());
        }
        return $query;
    }

	public function getReviewStatement($exp, $detector, $project, $version, $misuse, $name, $comment){
		return "INSERT INTO reviews (exp, detector, project, version, misuse, name, comment) VALUES (" . $this->pdo->quote($exp) . "," . $this->pdo->quote($detector) . "," . $this->pdo->quote($project) . "," . $this->pdo->quote($version) . "," . $this->pdo->quote($misuse) . "," . $this->pdo->quote($name) . "," . $this->pdo->quote($comment) . ");";
	}

	public function getReviewDeleteStatement($exp, $detector, $project, $version, $misuse, $name){
	    return "DELETE FROM reviews WHERE exp=" . $this->pdo->quote($exp) . " AND detector=" . $this->pdo->quote($detector) . " AND project=" . $this->pdo->quote($project) ." AND version=" . $this->pdo->quote($version) ." AND misuse=" . $this->pdo->quote($misuse) ." AND name=" . $this->pdo->quote($name) . ";";
    }

	public function deleteStatement($table, $project, $version){
		return "DELETE FROM " . $table . " WHERE identifier=" . $this->pdo->quote($project . "." . $version) . ";";
	}

	public function columnQuery($table){
		return "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=" . $this->pdo->quote($table) . ";";
	}

	public function getReviewFindingStatement($reviewId, $decision, $rank){
	    return "INSERT INTO review_findings (decision, review, rank) VALUES(" . $this->pdo->quote($decision) . ", ". $this->pdo->quote($reviewId) . "," . $this->pdo->quote($rank) . ");";

    }

    public function getReviewFinding($id, $rank){
        $query = [];
        try{
            $query = $this->pdo->query("SELECT * from review_findings WHERE review=" . $this->pdo->quote($id) . "AND rank=" . $this->pdo->quote($rank) . ";");
        }catch(PDOException $e){
            $this->logger->error("Error getReviewFinding: " . $e->getMessage());
        }
        if(!$query){
            return [];
        }
        foreach($query as $q){
           return $q;
        }
    }

    public function getReviewFindings($id){
        $query = [];
        try{
            $query = $this->pdo->query("SELECT * from review_findings WHERE review=" . $this->pdo->quote($id) . ";");
        }catch(PDOException $e){
            $this->logger->error("Error getReviewFindings: " . $e->getMessage());
        }
        if(!$query){
            return [];
        }
        $result = [];
        foreach($query as $q){
            $result[] =  $q;
        }
        return $result;
    }

    public function getTypes(){
        return $this->execQuery("SELECT * from types;");
    }

    public function execQuery($sql){
        $query = [];
        try{
            $query = $this->pdo->query($sql);
        }catch(PDOException $e){
            $this->logger->error("Error getTypes: " . $e->getMessage());
        }
        if(!$query){
            return [];
        }
        return $this->queryToArray($query);
    }

    public function queryToArray($query){
        if(!$query){
            return [];
        }
        $result = [];
        foreach($query as $q){
            $result[] =  $q;
        }
        return $result;
    }

    public function getTypeIdByName($name){
        $types = $this->execQuery("SELECT * from types WHERE name=" . $this->pdo->quote($name) . ";");
        foreach($types as $type){
            if($type['name'] === $name){
                return $type['id'];
            }
        }
        return 0;
    }

    public function getTypeNameById($id){
        $types = $this->execQuery("SELECT * from types WHERE id=" . $this->pdo->quote($id) . ";");
        foreach($types as $type){
            if($type['id'] === $id){
                return $type['name'];
            }
        }
        return "unknown";
    }

    public function getReviewTypes($id){
        $query = [];
        try{
            $query = $this->pdo->query("SELECT * from review_findings_type WHERE review_finding=". $this->pdo->quote($id) . ";");
        }catch(PDOException $e){
            $this->logger->error("Error getTypes: " . $e->getMessage());
        }
        if(!$query){
            return [];
        }
        $result = [];
        foreach($query as $q){
            $result[] = $this->getTypeNameById($q['type']);
        }
        return $result;
    }

    public function addReviewType($findingId, $type){
        return "INSERT INTO review_findings_type (review_finding, type) VALUES (". $this->pdo->quote($findingId). "," . $this->pdo->quote($type). ");";
    }

    public function getReviewFindingsDeleteStatement($findingId){
        return "DELETE FROM review_findings WHERE id=" . $this->pdo->quote($findingId) . ";";
    }

    public function getReviewFindingsTypeDelete($id){
        return "DELETE FROM review_findings_type WHERE review_finding=" . $this->pdo->quote($id) . ";";
    }
}