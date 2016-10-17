<?php

require_once 'sql/sql.php';

function get_table_name($ex, $dataset, $detector){
	return $ex . '_' . $dataset . '_' . $detector;
}

function get_json_names($obj){
	$columns = array();
	$columns[] = 'project';
	$columns[] = 'version';
	foreach($obj as $hit){
		foreach($hit as $key => $value){
			$columns[] = $key;
		}
		return $columns;
	}
	return $columns;
}

function validate_table_columns($table_columns, $obj){
	$names = get_json_names($obj);
	if(count($table_columns) == 0){
		return false;
	}
	return $table_columns === $names;
}

function handle_data($this, $table, $obj, $project, $version){
	$valid = validate_table_columns(get_table_columns($table), $obj);

    if(!$valid){
	    try{
			create_table($table, $obj);
		}catch(PDOException $e){
			$this->logger->info("could not create table " . $table);
			try{
				drop_table($table);
				create_table($table, $obj);
			}catch(PDOException $e){
				$this->logger->info("dropped, but still error " . $table);
			}
		}
	}

	foreach($obj as $hit){
		try{
			insert_entry($table, $project, $version, $hit);
		}catch(PDOException $e){
			$this->logger->info("insert failed " . $table);
		}
	}
}
