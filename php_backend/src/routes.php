<?php
require_once "src/Upload/FindingsUploader.php";
require_once "src/Upload/MetadataUploader.php";
require_once "src/Upload/ReviewUploader.php";

// Routes
$app->get('/', function ($request, $response, $args) use ($app) {
    return $app->helper->index_route($request, $args, $app, $this, $response, false);
});

$app->get('/impressum/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'impressum.html');
});

$app->get('/{exp:ex[1-3]}', function ($request, $response, $args) use ($app) {
    return $app->helper->experiment_route($request, $args, $app, $this, $response, false);
});

$app->get('/{exp:ex[1-3]}/{detector}', function ($request, $response, $args) use ($app) {
	return $app->helper->detect_route($request, $args, $app, $this, $response, false);
});

$app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}', function ($request, $response, $args) use ($app) {
    return $app->helper->review_route($args, $app, $this, $response, $request, false, false);
});

$app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}/{reviewer}', function ($request, $response, $args) use ($app) {
    return $app->helper->review_route($args, $app, $this, $response, $request, false, true);
});

$app->get('/stats', function ($request, $response, $args) use ($app) {
    $ex2_review_size = $request->getQueryParam("ex2_review_size", 20);
    return $app->helper->stats_route($this, $response, $args, $ex2_review_size);
});

$app->group('/private', function () use ($app, $settings) {

    $app->get('/', function ($request, $response, $args) use ($app) {
        return $app->helper->index_route($request, $args, $app, $this, $response, true);
    });

    $app->get('/status', function ($request, $response, $args) use ($app) {
        return $app->helper->review_status($request, $args, $app, $this, $response, false);
    });

    $app->get('/{exp:ex[1-3]}', function ($request, $response, $args) use ($app) {
        return $app->helper->experiment_route($request, $args, $app, $this, $response, true);
    });

    $app->get('/{exp:ex[1-3]}/{detector}', function ($request, $response, $args) use ($app) {
        return $app->helper->detect_route($request, $args, $app, $this, $response, true);
    });

    $app->post('/review/{exp:ex[1-3]}/{detector}', function ($request, $response, $args) use ($app) {
        $obj = $request->getParsedBody();
        $uploader = new ReviewUploader($app->db, $this->logger);
        $uploader->processReview($obj);
        return $response->withRedirect('../../' . $args['exp'] . "/" . $args['detector']);
    });

    $app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}', function ($request, $response, $args) use ($app) {
        return $app->helper->review_route($args, $app, $this, $response, $request, true, true);
    });

    $app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}/{reviewer}', function ($request, $response, $args) use ($app) {
        return $app->helper->review_route($args, $app, $this, $response, $request, false, true);
    });

    $app->get('/overview', function ($request, $response, $args) use ($app){
        $app->helper->overview_route($request, $args, $app, $this, $response);
    });

    $app->get('/todo', function ($request, $response, $args) use ($app){
        $app->helper->todo_route($request, $args, $app, $this, $response);
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
        if (!$project || !$version) {
            $this->logger->error("upload failed, could not read data " . dump($obj));
            return $response->withStatus(500);
        }
        $this->logger->info("uploading data for: " . $project . " version " . $version . " with " . count($hits) . " hits.");
        $uploader = new FindingsUploader($app->db, $this->logger);
        $uploader->processData($experiment, $obj, $obj->{'potential_hits'});
        $files = $request->getUploadedFiles();
        $this->logger->info("received " . count($files) . " files");
        if($files) {
            foreach ($files as $img) {
                $app->dir->handleImage($experiment, $obj->{'detector'}, $obj->{'project'}, $obj->{'version'}, $img);
            }
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
        $uploader = new MetadataUploader($app->db, $this->logger);
        foreach ($obj as $o) {
            $uploader->processMetaData($o);
        }
        return $response->withStatus(200);
    });

});
