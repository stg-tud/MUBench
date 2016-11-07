<?php
// Routes
function varDumpToString ($var)
{
    ob_start();
    var_dump($var);
    return ob_get_clean();
}

$app->get('/', function ($request, $response, $args) use ($settings) {
    return $this->renderer->render($response, 'index.phtml', array('experiments' => $settings['ex_template']));
});

$app->get('/impressum/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'impressum.html');
});

$app->get('/dataset/[{prefix}]', function ($request, $response, $args) use ($app, $settings) {
	$prefix = $args['prefix'];
	$data = $app->db->getDatasets($prefix);
	$template = $settings['ex_template'][split('[_]', $prefix)[0]];
    return $this->renderer->render($response, 'dataset.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'prefix' => $prefix));
});

$app->get('/experiment/[{prefix}]', function ($request, $response, $args) use ($app, $settings) {
	$prefix = $args['prefix'];
	$data = $app->db->getDetectors($prefix);
	$template = $settings['ex_template'][split('[_]', $prefix)[0]];
    return $this->renderer->render($response, 'experiment.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'prefix' => $prefix));
});

$app->get('/detect/[{experiment_detector}]', function ($request, $response, $args) use ($app) {
	$arr = split('[_]', $args['experiment_detector']);
	$exp = $arr[0];
	$detector = $arr[2];
	$test = [
	0 => [
			"project" => "aclang",
			"versions" => [
				["version" => "1",
				"findings" => 10,
				"items" => [
						["id" => "1", "type" => "missing/condition/null_check", "review" => "aclang.1.1"],
						["id" => "2", "type" => "missing/condition/null_check", "review" => "aclang.1.2"]
					]]
			]
		]
	];
	$this->logger->info(varDumpToString($app->db->getData($exp, $detector)));
	$this->logger->info(varDumpToString($app->db->getMetaData()));
	return $this->renderer->render($response, 'detector.phtml', array('detector' => $detector,'projects' => $test));
});

$app->post('/api/upload/[{experiment}]', function ($request, $response, $args) use ($app) {
	$obj = json_decode($request->getBody());
	$experiment = $args['experiment'];
	if($obj && ($experiment === "ex1" || $experiment === "ex2" || $experiment === "ex3")){
		foreach($obj as $d){
			$app->db->handleData($experiment, $d, $d->{'potential_hits'});
			//$app->dir->handleImage('ex1', $obj->{'project'}, $obj->{'version'}, $img);
			$this->logger->info($experiment);
		}	
	}
});

$app->post('/api/upload/misuse-metadata/', function ($request, $response, $args) use ($app) {
	$obj = json_decode($request->getUploadedFiles()['json']->getStream());
	foreach($obj as $o){
		$app->db->handleMetaData($o);
	}
});
