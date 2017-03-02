<?php
require_once "src/Upload/FindingsUploader.php";
require_once "src/Upload/MetadataUploader.php";
require_once "src/Upload/ReviewUploader.php";
require_once "src/Upload/SnippetUploader.php";

// Routes
$app->get('/', function ($request, $response, $args) use ($app) {
    return $app->helper->index_route($args, $this, $response, false);
});

$app->get('/impressum/', function ($request, $response, $args) use ($app) {
    return $this->renderer->render($response, 'impressum.html');
});

$app->get('/{exp:ex[1-3]}', function ($request, $response, $args) use ($app) {
    return $app->helper->experiment_route($args, $this, $response, false);
});

$app->get('/{exp:ex[1-3]}/{detector}', function ($request, $response, $args) use ($app) {
	return $app->helper->detect_route($args, $this, $response, false);
});

$app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}', function ($request, $response, $args) use ($app) {
    return $app->helper->review_route($args, $this, $response, false, false);
});

$app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}/{reviewer}', function ($request, $response, $args) use ($app) {
    return $app->helper->review_route($args, $this, $response, false, true);
});

$app->get('/stats', function ($request, $response, $args) use ($app) {
    $ex2_review_size = $request->getQueryParam("ex2_review_size", 20);
    return $app->helper->stats_route($this, $response, $args, $ex2_review_size);
});

$app->group('/private', function () use ($app, $settings) {

    $app->get('/', function ($request, $response, $args) use ($app) {
        return $app->helper->index_route($args, $this, $response);
    });

    $app->get('/status', function ($request, $response, $args) use ($app) {
        return $app->helper->review_status($request, $args, $app, $this, $response);
    });

    $app->get('/{exp:ex[1-3]}', function ($request, $response, $args) use ($app) {
        return $app->helper->experiment_route($args, $this, $response);
    });

    $app->get('/{exp:ex[1-3]}/{detector}', function ($request, $response, $args) use ($app) {
        return $app->helper->detect_route($args, $this, $response);
    });

    $app->post('/review/{exp:ex[1-3]}/{detector}', function ($request, $response, $args) use ($app) {
        $obj = $request->getParsedBody();
        $uploader = new ReviewUploader($app->db, $this->logger);
        $uploader->processReview($obj);
        if(strcmp($obj["origin"], "") !== 0){
            return $response->withRedirect('../../../' . $obj["origin"]);
        }
        return $response->withRedirect('../../' . $args['exp'] . "/" . $args['detector']);
    });

    $app->post('/snippet', function ($request, $response, $args) use ($app) {
        $obj = $request->getParsedBody();
        $uploader = new SnippetUploader($app->db, $this->logger);
        $uploader->processSnippet($obj);
        return $response->withRedirect('../' . $obj['path']);
    });

    $app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}', function ($request, $response, $args) use ($app) {
        return $app->helper->review_route($args, $this, $response, true);
    });

    $app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}/{reviewer}', function ($request, $response, $args) use ($app) {
        return $app->helper->review_route($args, $this, $response, true);
    });

    $app->get('/overview', function ($request, $response, $args) use ($app){
        $app->helper->overview_route($args, $this, $response);
    });

    $app->get('/todo', function ($request, $response, $args) use ($app){
        $app->helper->todo_route($args, $this, $response);
    });
});

$app->group('/api', function () use ($app) {

    $app->post('/upload/[{experiment:ex[1-3]}]', function ($request, $response, $args) use ($app) {
        $experiment = $args['experiment'];
        $obj = parseJsonBody($request);
        if (!$obj) {
            return error_response($response, $this->logger, 400, "empty: " . dump($request->getBody()));
        }
        $detector = $obj->{'detector'};
        if (!$detector) {
            return error_response($response, $this->logger, 400, "no detector: " . dump($obj));
        }
        $project = $obj->{'project'};
        if (!$project) {
            return error_response($response, $this->logger, 400, "no project: " . dump($obj));
        }
        $version = $obj->{'version'};
        if (!$version) {
            return error_response($response, $this->logger, 400, "no version: " . dump($obj));
        }
        $hits = $obj->{'potential_hits'};
        $this->logger->info("received data for '" . $experiment . "', '" . $project . "." . $version . "' with " . count($hits) . " potential hits.");
        $uploader = new FindingsUploader($app->db, $this->logger);
        $uploader->processData($experiment, $obj, $hits);
        $files = $request->getUploadedFiles();
        $this->logger->info("received " . count($files) . " files");
        if($files) {
            foreach ($files as $img) {
                $app->dir->handleImage($experiment, $detector, $project, $version, $img);
            }
        }
        return $response->withStatus(200);
    });

    $app->post('/upload/metadata', function ($request, $response, $args) use ($app) {
        $obj = parseJsonBody($request);
        if (!$obj) {
            return error_response($response, $this->logger, 400, "empty: " . dump($request->getBody()));
        }
        $uploader = new MetadataUploader($app->db, $this->logger);
        foreach ($obj as $o) {
            $uploader->processMetaData($o);
        }
        return $response->withStatus(200);
    });

});

function parseJsonBody($request)
{
    $requestBody = $request->getParsedBody();
    $body = json_decode($requestBody);
    if ($body) return $body;
    $body = json_decode($request->getBody());
    if ($body) return $body;
    $body = json_decode($_POST["data"]);
    return $body;
}

function dump($obj) {
    return print_r($obj, true);
}

function error_response($response, $logger, $code, $message) {
    $logger->error($message);
    return $response->withStatus($code)->write($message);
}
