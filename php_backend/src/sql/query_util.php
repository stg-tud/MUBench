<?php

function build_columns($obj){
	$output = ", id int NOT NULL";
	foreach($obj as $hit){
		foreach($hit as $key => $value){
			if($value != "id"){
				$output = $output . "," . $key . " TEXT NOT NULL";
			}
		}
		return $output;
	}
}

function get_insert_statement($table, $project, $version, $obj){
	$output = "INSERT INTO " . $table . " VALUES ('" . $project . "','" . $version;
	foreach($obj as $value){
		$output = $output . "','" . $value;
	}
	return $output . "');";
}

function get_delete_statement($table, $id){
	return "DELETE FROM " . $table . " WHERE id=" . $id . ";";
}

function column_query($table){
	return "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='" . $table . "';";
}