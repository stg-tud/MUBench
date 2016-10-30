<?php
// Routes

$app->get('/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'index.phtml', array('name' => 'Test'));
});

$app->post('/api/upload/ex1', function ($request, $response, $args) use ($app) {
	$obj = json_decode($request->getBody());
	if($obj){
		foreach($obj as $d){
			$app->db->handleData('ex1', $d, $d->{'findings'});
			//$app->dir->handleImage('ex1', $obj->{'project'}, $obj->{'version'}, $img);
			$this->logger->info('ex1');
		}	
	}
});

$app->post('/api/upload/ex2', function ($request, $response, $args) use ($app){
	$obj = json_decode($request->getBody());
	if($obj){
		foreach($obj as $d){
			$app->db->handleData('ex2', $d, $d->{'findings'});
			//$app->dir->handleImage('ex1', $obj->{'project'}, $obj->{'version'}, $img);
			$this->logger->info('ex2');
		}	
	}
});

$app->post('/api/upload/ex3', function ($request, $response, $args) use ($app){
    $obj = json_decode($request->getBody());
	if($obj){
		foreach($obj as $d){
			$app->db->handleData('ex3', $d, $d->{'findings'});
			//$app->dir->handleImage('ex1', $obj->{'project'}, $obj->{'version'}, $img);
			$this->logger->info('ex3');
		}	
	}
});

$app->post('/api/upload/misuse-metadata/', function ($request, $response, $args) {

});
