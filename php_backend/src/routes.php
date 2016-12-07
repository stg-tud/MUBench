<?php
// Routes

function dump($var){
	ob_start();
	var_dump($var);
	return  ob_get_clean();
}

function detect_route($args, $app, $r, $response, $logged){
	$exp = $args['exp'];
	$dataset = $args['dataset'];
	$detector = $args['detector'];
	if(!($exp === "ex1" || $exp === "ex2" || $exp === "ex3") || $detector == "" || $dataset == ""){
        return $response->withStatus(404);
	}
	$stats = $app->data->getIndex($exp, $dataset, $detector);
	return $r->renderer->render($response, 'detector.phtml', array('logged' => $logged, 'exp' => $exp, 'dataset' => $dataset, 'detector' => $detector,'projects' => $stats));
}

function review_route($args, $app, $r, $response, $request, $logged, $review_flag){
    $exp = $args['exp'];
    $set = $args['dataset'];
    $detector = $args['detector'];
    $project = $args['project'];
    $version = $args['version'];
    $misuse = $args['misuse'];
    $data = $app->data->getMetadata($misuse);
    $patterns = $app->data->getPatterns($misuse);
    $hits = $app->data->getHits($exp . "_" . $set . "_" . $detector, $project, $version, $misuse, $exp);
    $reviewer = "";
    $review = NULL;
    if ($review_flag && !$logged) {
        $reviewer = $args['reviewer'];
    } else if ($review_flag && $logged) {
        $reviewer = $request->getServerParams()['PHP_AUTH_USER'];
    }
    $review = $app->data->getReview($exp, $set, $detector, $project, $version, $misuse, $reviewer);
    return $r->renderer->render($response, 'review.phtml', array('name' => $reviewer, 'review' => $review, 'set' => $set, 'logged' => $logged, 'exp' => $exp, 'detector' => $detector, 'version' => $version, 'project' => $project, 'misuse' => $misuse, 'desc' => $data['description'], 'fix_desc' => $data['fix_description'], 'diff_url' => $data['diff_url'], 'violation_types' => $data['violation_types'], 'file' => ($exp == "ex2" ? $hits[0]['file'] : $data['file']), 'method' => ($exp == "ex2" ? $hits[0]['method'] : $data['method']), 'code' => $hits[0]['target_snippets'], 'line' => $hits[0]['line'], 'pattern_code' => $patterns['code'], 'pattern_line' => $patterns['line'], 'pattern_name' => $patterns['name'], 'hits' => $hits));
}

$app->get('/', function ($request, $response, $args) use ($settings) {
    return $this->renderer->render($response, 'index.phtml', array('experiments' => $settings['ex_template']));
});

$app->get('/impressum/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'impressum.html');
});

$app->get('/{prefix}', function ($request, $response, $args) use ($app, $settings) {
	$prefix = $args['prefix'];
	$data = $app->data->getDatasets($prefix);
	$template = $settings['ex_template'][$prefix];
    return $this->renderer->render($response, 'dataset.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'prefix' => $prefix));
});

$app->get('/{exp:ex[1-3]}/{dataset}', function ($request, $response, $args) use ($app, $settings) {
    $exp = $args['exp'];
    $dataset = $args['dataset'];
	$data = $app->data->getDetectors($exp . "_" . $dataset);
	$template = $settings['ex_template'][$exp];
    return $this->renderer->render($response, 'experiment.phtml', array('data' => $data, 'id' => $template['id'], 'title' => $template['title'], 'exp' => $exp, 'dataset' => $dataset));
});

$app->get('/{exp:ex[1-3]}/{dataset}/{detector}', function ($request, $response, $args) use ($app) {
	return detect_route($args, $app, $this, $response, false);
});

$app->get('/{exp:ex[1-3]}/{dataset}/{detector}/{project}/{version}/{misuse}', function ($request, $response, $args) use ($app) {
    return review_route($args, $app, $this, $response, $request, false, false);
});

$app->get('/{exp:ex[1-3]}/{dataset}/{detector}/{project}/{version}/{misuse}/{reviewer}', function ($request, $response, $args) use ($app) {
    return review_route($args, $app, $this, $response, $request, false, true);
});

$app->group('/private', function () use ($app) {

    $app->get('/{exp:ex[1-3]}/{dataset}/{detector}', function ($request, $response, $args) use ($app) {
        return detect_route($args, $app, $this, $response, true);
    });

    $app->post('/review/{exp:ex[1-3]}/{dataset}/{detector}', function ($request, $response, $args) use ($app) {
        $obj = $request->getParsedBody();
        $app->upload->processReview($obj);
        return $response->withRedirect('../../../' . $args['exp'] . "/" . $args['dataset'] . "/" . $args['detector']);
    });

    $app->get('/{exp:ex[1-3]}/{dataset}/{detector}/{project}/{version}/{misuse}', function ($request, $response, $args) use ($app) {
        return review_route($args, $app, $this, $response, $request, true, true);
    });

    $app->get('/{exp:ex[1-3]}/{dataset}/{detector}/{project}/{version}/{misuse}/{reviewer}', function ($request, $response, $args) use ($app) {
        return review_route($args, $app, $this, $response, $request, false, true);
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
        foreach ($request->getUploadedFiles() as $img) {
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
