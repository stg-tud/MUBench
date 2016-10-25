<?php
// Routes

$app->get('/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'index.phtml', array('name' => 'Test'));
});

$app->post('/api/upload/ex1', function ($request, $response, $args) use ($app) {
	$json = $request->getUploadedFiles()['json'];
	$obj = json_decode($json->getStream());
	//$app->db->handleData('ex1', $obj, $obj->{'potential_hits'});
	$app->dir->handleImage('ex1', $obj->{'project'}, $obj->{'version'});
	$this->logger->info('ex1');
});

$app->post('/api/upload/ex2', function ($request, $response, $args) use ($app){
	$this->logger->info('ex2');
	$files = $request->getUploadedFiles();
	$img = $files['image'];
	$json = $files['json'];
	$img->moveTo('./upload/ex2/'. $img->getClientFilename());
    $obj = json_decode($json->getStream());
	$app->db->handleData('ex2', $obj, $obj->{'findings'});
});

$app->post('/api/upload/ex3', function ($request, $response, $args) use ($app){
	$files = $request->getUploadedFiles();
	$img = $files['image'];
	$json = $files['json'];
	$img->moveTo('./upload/ex3/'. $img->getClientFilename());
    $obj = json_decode($json->getStream());
    $app->db->handleData('ex3', $obj, $obj->{'potential_hits'});
});

$app->post('/api/upload/misuse-metadata/', function ($request, $response, $args) {

});
