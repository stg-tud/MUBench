<?php

class UploadProcessor {

	private $db;

	function __construct($db){
		$this->db = $db;
	}

	public function handleData($ex, $obj, $obj_array){
		$table = $this->db->getTableName($ex, $obj->{'dataset'}, $obj->{'detector'});
		$project = $obj->{'project'};
		$version = $obj->{'version'};
		$runtime = $obj->{'runtime'};
		$result = $obj->{'result'};
		$findings = $obj->{'number_of_findings'};
		$statements = [];
		$statements[] = $this->db->getStatDeleteStatement($table, $project, $version);
		$statements[] = $this->db->getStatStatement($table, $project, $version, $result, $runtime, $findings);
		$columns = $this->db->getTableColumns($table);
		$obj_columns = $this->getJsonNames($obj_array);
		if(count($columns) == 0){
			$statements[] = $this->db->createTableStatement($table, $obj_array);
		}
		$statements[] = $this->db->deleteStatement($table, $project, $version);
		$columns = $this->db->getTableColumns($table);
		foreach($obj_columns as $c){
			$add = true;
			foreach($columns as $oc){
				if($c == $oc){
					$add = false;
					break;
				}
			}
			if($add){
				$statements[] = $this->db->addColumnStatement($table, $c);
			}
		}
		foreach($obj_array as $hit){
			$statements[] = $this->db->insertStatement($table, $project, $version, $hit);
		}
		$this->db->execStatements($statements);
	}

	public function handleMetaData($json){
		$statements = [];
		$statements[] = $this->db->deleteMetadata($json->{'misuse'});
		$statements[] = $this->db->insertMetadata($json->{'misuse'},$json->{'description'}, $json->{'fix_description'}, $this->arrayToString($json->{'violation_types'}), $json->{'location'}->{'file'}, $json->{'location'}->{'method'}, $json->{'code'});
		$this->db->execStatements($statements);
	}	

	public function arrayToString($json){
		$out = $json[0];
		for($i = 1; $i < count($json); $i++){
			$out = $out . ';' . $json[$i];
		}
		return $out;
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

}