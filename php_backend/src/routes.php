<?php
// Routes
$app->get('/', function ($request, $response, $args) use ($settings) {
    return $this->renderer->render($response, 'index.phtml', array('experiments' => $settings['ex_template']));
});

$app->get('/impressum/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'impressum.html');
});

$app->get('/{exp:ex[1-3]}', function ($request, $response, $args) use ($app, $settings) {
	$prefix = $args['exp'];
	$data = $app->data->getDatasets($prefix);
	$template = $settings['ex_template'][$prefix];
    return $this->renderer->render($response, 'dataset.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'prefix' => $prefix));
});

$app->get('/{exp:ex[1-3]}/{dataset}', function ($request, $response, $args) use ($app, $settings) {
    $exp = $args['exp'];
    $dataset = $args['dataset'];
	$data = $app->data->getDetectors($exp . "_" . $dataset);
	if(!$data || emtpy($data)){
	    return $response->withStatus(404);
    }
	$template = $settings['ex_template'][$exp];
    return $this->renderer->render($response, 'experiment.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'exp' => $exp, 'dataset' => $dataset));
});

$app->get('/{exp:ex[1-3]}/{dataset}/{detector}', function ($request, $response, $args) use ($app) {
	return $app->helper->detect_route($args, $app, $this, $response, false);
});

$app->get('/{exp:ex[1-3]}/{dataset}/{detector}/{project}/{version}/{misuse}', function ($request, $response, $args) use ($app) {
    return $app->helper->review_route($args, $app, $this, $response, $request, false, false);
});

$app->get('/{exp:ex[1-3]}/{dataset}/{detector}/{project}/{version}/{misuse}/{reviewer}', function ($request, $response, $args) use ($app) {
    return $app->helper->review_route($args, $app, $this, $response, $request, false, true);
});

$app->group('/private', function () use ($app) {

    $app->get('/{exp:ex[1-3]}/{dataset}/{detector}', function ($request, $response, $args) use ($app) {
        return $app->helper->detect_route($args, $app, $this, $response, true);
    });

    $app->post('/review/{exp:ex[1-3]}/{dataset}/{detector}', function ($request, $response, $args) use ($app) {
        $obj = $request->getParsedBody();
        $app->upload->processReview($obj);
        return $response->withRedirect('../../../' . $args['exp'] . "/" . $args['dataset'] . "/" . $args['detector']);
    });

    $app->get('/{exp:ex[1-3]}/{dataset}/{detector}/{project}/{version}/{misuse}', function ($request, $response, $args) use ($app) {
        return $app->helper->review_route($args, $app, $this, $response, $request, true, true);
    });

    $app->get('/{exp:ex[1-3]}/{dataset}/{detector}/{project}/{version}/{misuse}/{reviewer}', function ($request, $response, $args) use ($app) {
        return $app->helper->review_route($args, $app, $this, $response, $request, false, true);
    });

});

$app->group('/api', function () use ($app) {

    $app->post('/upload/[{experiment:ex[1-3]}]', function ($request, $response, $args) use ($app) {
        $obj = json_decode($request->getParsedBody());
        $experiment = $args['experiment'];
        if (!$obj) {
            $obj = json_decode($request->getBody());
        }
        if (!$obj) {
            $obj = json_decode($_POST["data"]);
        }
        if (!$obj) {
            $this->logger->error("upload failed, object empty " . dump($request->getParsedBody()));
            return $response->withStatus(500);
        }
        $project = $obj->{'project'};
        $version = $obj->{'version'};
        $hits = $obj->{'potential_hits'};
        if (!$hits || !$project || !$version) {
            $this->logger->error("upload failed, could not read data " . dump($obj));
            return $response->withStatus(500);
        }
        $this->logger->info("uploading data for: " . $project . " version " . $version . " with " . count($hits) . " hits.");
        $app->upload->handleData($experiment, $obj, $obj->{'potential_hits'});
        $app->dir->deleteOldImages($experiment, $obj->{'project'}, $obj->{'version'});
        $files = $request->getUploadedFiles();
        $this->logger->info("Received " . count($files) . " files");
        foreach ($files as $img) {
            $app->dir->handleImage($experiment, $obj->{'project'}, $obj->{'version'}, $img);
        }
        return $response->withStatus(200);
    });

    $app->post('/upload/metadata', function ($request, $response, $args) use ($app) {
        $obj = json_decode($request->getBody());
        if (!$obj) {
            $obj = json_decode($request->getParsedBody());
        }
        if (!$obj) {
            $obj = json_decode($_POST["data"]);
        }
        if (!$obj) {
            $this->logger->error("upload of metadata failed, object empty: " . dump($request->getBody()));
            return $response->withStatus(500);
        }
        foreach ($obj as $o) {
            $app->upload->handleMetaData($o);
        }
        return $response->withStatus(200);
    });

});
