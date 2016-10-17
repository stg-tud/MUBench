<?php
// Routes
require 'util.php';

$app->get('/', function ($request, $response, $args) {
    return $this->renderer->render($response, 'index.phtml', array('name' => 'World'));
});

$app->post('/api/upload/ex1/', function ($request, $response, $args) {
	$files = $request->getUploadedFiles();
	$img = $files['image'];
	$json = $files['json'];
	
	$img->moveTo('./upload/ex1/'. $img->getClientFilename());
    $obj = json_decode($json->getStream());

    $table = get_table_name('ex1', $obj->{'dataset'}, $obj->{'detector_name'});
	handle_data($this, $table, $obj->{'potential_hits'}, $obj->{'project'}, $obj->{'version'});
});

$app->post('/api/upload/ex2/', function ($request, $response, $args) {
	$files = $request->getUploadedFiles();
	$img = $files['image'];
	$json = $files['json'];

	$img->moveTo('./upload/ex2/'. $img->getClientFilename());
    $obj = json_decode($json->getStream());

    $table = get_table_name('ex2', $obj->{'dataset'}, $obj->{'detector_name'});
	handle_data($this, $table, $obj->{'findings'}, $obj->{'project'}, $obj->{'version'});
});

$app->post('/api/upload/ex3/', function ($request, $response, $args) {
	$files = $request->getUploadedFiles();
	$img = $files['image'];
	$json = $files['json'];

	$img->moveTo('./upload/ex3/'. $img->getClientFilename());
    $obj = json_decode($json->getStream());

    $table = get_table_name('ex3', $obj->{'dataset'}, $obj->{'detector_name'});
	handle_data($this, $table, $obj->{'potential_hits'}, $obj->{'project'}, $obj->{'version'});
});

$app->post('/api/upload/misuse-metadata/', function ($request, $response, $args) {

});