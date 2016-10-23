<?php

require_once 'query_util.php';

use \Slim\Middleware\HttpBasicAuthentication\PdoAuthenticator;

function get_db_connection(){
	$servername = "127.0.0.1";
	$username = "root";
	$password = "mubench";
	$db_name = "mubench";

	$pdo = new PDO("mysql:host=$servername;dbname=mubench", $username, $password);
	$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

	return $pdo;
}

function create_table($table, $obj){
	$db = get_db_connection();
	$sql = 'CREATE TABLE ' . $table . '( project TEXT NOT NULL, version TEXT NOT NULL' . build_columns($obj) . ', PRIMARY KEY (id));';
    $status = $db->exec($sql);
}

function drop_table($table){
	$db = get_db_connection();
    $status = $db->exec("DROP TABLE " . $table);
}

function get_table_columns($table){
	$db = get_db_connection();
	$sql = column_query($table);
    try{
    	$query = $db->query($sql);
	}catch(PDOException $e){
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

function insert_entry($table, $project, $version, $hit){
	$db = get_db_connection();
	$delete_sql = get_delete_statement($table, $hit->{'id'});
	$sql = get_insert_statement($table, $project, $version, $hit);
	$status = $db->exec($delete_sql);
	$status = $db->exec($sql);
}


