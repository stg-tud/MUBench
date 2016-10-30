<?php
// Routes
function varDumpToString ($var)
{
    ob_start();
    var_dump($var);
    return ob_get_clean();
}

$app->get('/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'index.phtml', array('name' => 'Test'));
});

$app->get('/impressum/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'impressum.html');
});

$app->get('/ex/[{experiment}]', function ($request, $response, $args) use ($app, $settings) {
	$experiment = $args['experiment'];
	$detectors = $app->db->getDetectors($experiment);
	$template = $settings['ex_template'][$experiment];
    return $this->renderer->render($response, 'ex.phtml', array('detectors' => $detectors, 'id' => $template['id'], 'title' => $template['title']));
});

$app->post('/api/upload/[{experiment}]', function ($request, $response, $args) use ($app) {
	$obj = json_decode($request->getBody());
	$experiment = $args['experiment'];
	if($obj && ($experiment === "ex1" || $experiment === "ex2" || $experiment === "ex3")){
		foreach($obj as $d){
			$app->db->handleData($experiment, $d, $d->{'findings'});
			//$app->dir->handleImage('ex1', $obj->{'project'}, $obj->{'version'}, $img);
			$this->logger->info($experiment);
		}	
	}
});

$app->post('/api/upload/misuse-metadata/', function ($request, $response, $args) {

});
