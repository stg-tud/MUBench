<?php
// Routes

$app->get('/', function ($request, $response, $args) use ($settings) {
    return $this->renderer->render($response, 'index.phtml', array('experiments' => $settings['ex_template']));
});

$app->get('/impressum/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'impressum.html');
});

$app->get('/dataset/[{prefix}]', function ($request, $response, $args) use ($app, $settings) {
	$prefix = $args['prefix'];
	$data = $app->data->getDatasets($prefix);
	$template = $settings['ex_template'][split('[_]', $prefix)[0]];
    return $this->renderer->render($response, 'dataset.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'prefix' => $prefix));
});

$app->get('/experiment/[{prefix}]', function ($request, $response, $args) use ($app, $settings) {
	$prefix = $args['prefix'];
	$data = $app->data->getDetectors($prefix);
	$template = $settings['ex_template'][split('[_]', $prefix)[0]];
    return $this->renderer->render($response, 'experiment.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'prefix' => $prefix));
});

$app->get('/detect/[{detector}]', function ($request, $response, $args) use ($app) {
	$arr = split('[_]', $args['detector']);
	$exp = $arr[0];
	$detector = $arr[2];
	if(count($arr) != 3 || !($exp === "ex1" || $exp === "ex2" || $exp === "ex3") || $detector == ""){
		return;
	}
	$data = $app->data->getPotentialHitsIndex($args['detector']);
	return $this->renderer->render($response, 'detector.phtml', array('identifier' => $args['detector'], 'detector' => $detector,'projects' => $data));
});

$app->get('/review/[{misuse}]', function ($request, $response, $args) use ($app) {
	return $this->renderer->render($response, 'review.phtml');
});

$app->post('/api/upload/[{experiment}]', function ($request, $response, $args) use ($app) {
	$obj = json_decode($_POST['data']);
	$experiment = $args['experiment'];
	if($obj && ($experiment === "ex1" || $experiment === "ex2" || $experiment === "ex3")){
		$f = [];
		foreach($obj as $d){
			foreach($d->{'potential_hits'} as $h){
				$f[$h->{'pattern_violation'}] = $d->{'project'} . "/" . $d->{'version'};
			}
			$this->logger->info("HALLO");
			$app->upload->handleData($experiment, $d, $d->{'potential_hits'});
			$this->logger->info("HALLO2");
		}
		foreach($request->getUploadedFiles() as $img){
			$app->dir->handleImage($experiment, $f[$img->getClientFilename()], $img);
		}
	}
});

$app->post('/api/upload/misuse-metadata/', function ($request, $response, $args) use ($app) {
	$obj = json_decode($request->getUploadedFiles()['json']->getStream());
	foreach($obj as $o){
		$app->upload->handleMetaData($o);
	}
});
