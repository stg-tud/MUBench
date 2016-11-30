<?php
// Routes

function dump($var){
	ob_start();
	var_dump($var);
	return  ob_get_clean();
}

function detect_route($args, $app, $r, $response, $logged){
	$arr = explode("_", $args['detector']);
	$exp = $arr[0];
	$detector = $arr[2];
	if(count($arr) != 3 || !($exp === "ex1" || $exp === "ex2" || $exp === "ex3") || $detector == ""){
        return $response->withStatus(404);
	}
	$stats = $app->data->getIndex($args['detector'], $exp);
	return $r->renderer->render($response, 'detector.phtml', array('logged' => $logged, 'exp' => $exp, 'identifier' => $args['detector'], 'detector' => $detector,'projects' => $stats));
}

$app->get('/', function ($request, $response, $args) use ($settings) {
    return $this->renderer->render($response, 'index.phtml', array('experiments' => $settings['ex_template']));
});

$app->get('/impressum/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'impressum.html');
});

$app->get('/dataset/[{prefix}]', function ($request, $response, $args) use ($app, $settings) {
	$prefix = $args['prefix'];
	$data = $app->data->getDatasets($prefix);
	$template = $settings['ex_template'][explode("_", $prefix)[0]];
    return $this->renderer->render($response, 'dataset.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'prefix' => $prefix));
});

$app->get('/experiment/[{prefix}]', function ($request, $response, $args) use ($app, $settings) {
	$prefix = $args['prefix'];
	$data = $app->data->getDetectors($prefix);
	$template = $settings['ex_template'][explode("_", $prefix)[0]];
    return $this->renderer->render($response, 'experiment.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'prefix' => $prefix));
});

$app->get('/detect/[{detector}]', function ($request, $response, $args) use ($app) {
	return detect_route($args, $app, $this, $response, false);
});

$app->get('/review/[{misuse}]', function ($request, $response, $args) use ($app) {
	$arr = explode("_", $args['misuse']);
	$exp = $arr[0];
	$set = $arr[1];
	$detector = $arr[2];
	$project = $arr[3];
	$version = $arr[4];
	$misuse = $arr[5];
	if(count($arr) < 6  || $detector == ""){
        return $response->withStatus(404);
	}
	$data = $app->data->getMetadata($misuse);
	$patterns = $app->data->getPatterns($misuse);
	$hits = $app->data->getHits($exp . "_" . $set . "_" . $detector, $project, $version, $misuse, $exp);
	return $this->renderer->render($response, 'review.phtml', array('logged' => false, 'set' => $set, 'exp' => $exp, 'detector' => $detector, 'version' => $version, 'project' => $project, 'misuse' => $misuse, 'desc' => $data['description'], 'fix_desc' => $data['fix_description'], 'diff_url' => $data['diff_url'], 'violation_types' => $data['violation_types'], 'file' => ($exp == "ex2" ? $hits[0]['file'] : $data['file']), 'method' => ($exp == "ex2" ? $hits[0]['method'] : $data['method']), 'code' => $hits[0]['target_snippets'], 'line' => $hits[0]['line'], 'pattern_code' => $patterns['code'], 'pattern_line' => $patterns['line'], 'pattern_name' => $patterns['name'], 'hits' => $hits));
});

$app->get('/logged/detect/[{detector}]', function ($request, $response, $args) use ($app) {
	return detect_route($args, $app, $this, $response, true);
});

$app->post('/logged/review_form/[{detector}]', function ($request, $response, $args) use ($app) {
	$obj = $request->getParsedBody();
	$app->upload->processReview($obj);
	return  $response->withRedirect('/site/index.php/logged/detect/' . $args['detector']);
});

$app->get('/logged/review/[{misuse}]', function ($request, $response, $args) use ($app) {
	$arr = explode("_", $args['misuse']);
	$exp = $arr[0];
	$set = $arr[1];
	$detector = $arr[2];
	$project = $arr[3];
	$version = $arr[4];
	$misuse = $arr[5];
	if(count($arr) != 6  || $detector == ""){
		return $response->withStatus(404);
	}
	$review = $app->data->getReview($request->getServerParams()['PHP_AUTH_USER'], $args['misuse']);
	$data = $app->data->getMetadata($misuse);
	$patterns = $app->data->getPatterns($misuse);
	$hits = $app->data->getHits($exp . "_" . $set . "_" . $detector, $project, $version, $misuse, $exp);
	return $this->renderer->render($response, 'review.phtml', array('review' => $review, 'set' => $set, 'logged' => true, 'name' => $request->getServerParams()['PHP_AUTH_USER'], 'exp' => $exp, 'detector' => $detector, 'version' => $version, 'project' => $project, 'misuse' => $misuse, 'desc' => $data['description'], 'fix_desc' => $data['fix_description'], 'diff_url' => $data['diff_url'], 'violation_types' => $data['violation_types'], 'file' => ($exp == "ex2" ? $hits[0]['file'] : $data['file']), 'method' => ($exp == "ex2" ? $hits[0]['method'] : $data['method']), 'code' => $hits[0]['target_snippets'], 'line' => $hits[0]['line'], 'pattern_code' => $patterns['code'], 'pattern_line' => $patterns['line'], 'pattern_name' => $patterns['name'], 'hits' => $hits));
});

$app->post('/api/upload/[{experiment:ex[1-3]}]', function ($request, $response, $args) use ($app) {
	$obj = json_decode($request->getParsedBody()["data"]);
	$experiment = $args['experiment'];
	if(!$obj){
		$this->logger->error("upload failed, object empty " . dump($request->getParsedBody()));
		return $response->withStatus(500);
	}
    $app->upload->handleData($experiment, $obj, $obj->{'potential_hits'});
	$app->dir->deleteOldImages($experiment, $obj->{'project'}, $obj->{'version'});
    foreach($request->getUploadedFiles() as $img){
        $app->dir->handleImage($experiment, $obj->{'project'}, $obj->{'version'}, $img);
    }
	return $response->withStatus(200);
});

$app->post('/api/upload/metadata', function ($request, $response, $args) use ($app) {
	$obj = json_decode($request->getParsedBody()["data"]);
	if(!$obj){
		$this->logger->error("upload of metadata failed, object empty: " . dump($request->getParsedBody()));
		return $response->withStatus(500);
	}
	foreach($obj as $o){
		$app->upload->handleMetaData($o);
	}
	return $response->withStatus(200);
});
