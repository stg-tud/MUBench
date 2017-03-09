<?php

use MuBench\ReviewSite\Controller\FindingsUploader;
use MuBench\ReviewSite\Controller\MetadataUploader;
use MuBench\ReviewSite\Controller\ReviewUploader;
use MuBench\ReviewSite\Controller\SnippetUploader;
use Slim\Http\Request;
use Slim\Http\Response;

require_once "route_utils.php";

// Routes
$app->get('/',
    function (Request $request, Response $response, array $args) use ($app) {
        return $app->helper->index_route($args, $this, $response, false);
    });

$app->get('/{exp:ex[1-3]}',
    function (Request $request, Response $response, array $args) use ($app) {
        return $app->helper->experiment_route($args, $this, $response, false);
    });

$app->get('/{exp:ex[1-3]}/{detector}',
    function (Request $request, Response $response, array $args) use ($app) {
        return $app->helper->detect_route($args, $this, $response, false);
    });

$app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}',
    function (Request $request, Response $response, array $args) use ($app) {
        return $app->helper->review_route($args, $this, $response, false, false);
    });

$app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}/{reviewer}',
    function (Request $request, Response $response, array $args) use ($app) {
        return $app->helper->review_route($args, $this, $response, false, true);
    });

$app->get('/stats',
    function (Request $request, Response $response, array $args) use ($app) {
        $ex2_review_size = $request->getQueryParam("ex2_review_size", 20);
        return $app->helper->stats_route($this, $response, $args, $ex2_review_size);
    });

$app->group('/private', function () use ($app, $settings) {

    $app->get('/',
        function (Request $request, Response $response, array $args) use ($app) {
            return $app->helper->index_route($args, $this, $response);
        });

    $app->get('/status',
        function (Request $request, Response $response, array $args) use ($app) {
            return $app->helper->review_status($request, $args, $app, $this, $response);
        });

    $app->get('/{exp:ex[1-3]}',
        function (Request $request, Response $response, array $args) use ($app) {
            return $app->helper->experiment_route($args, $this, $response);
        });

    $app->get('/{exp:ex[1-3]}/{detector}',
        function (Request $request, Response $response, array $args) use ($app) {
            return $app->helper->detect_route($args, $this, $response);
        });

    $app->post('/review/{exp:ex[1-3]}/{detector}',
        function (Request $request, Response $response, array $args) use ($app) {
            $obj = $request->getParsedBody();
            $uploader = new ReviewUploader($app->db, $this->logger);
            $uploader->processReview($obj);
            if (strcmp($obj["origin"], "") !== 0) {
                return $response->withRedirect('../../../' . $obj["origin"]);
            }
            return $response->withRedirect('../../' . $args['exp'] . "/" . $args['detector']);
        });

    $app->post('/snippet',
        function (Request $request, Response $response, array $args) use ($app) {
            $obj = $request->getParsedBody();
            $uploader = new SnippetUploader($app->db, $this->logger);
            $uploader->processSnippet($obj);
            return $response->withRedirect('../' . $obj['path']);
        });

    $app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}',
        function (Request $request, Response $response, array $args) use ($app) {
            return $app->helper->review_route($args, $this, $response, true);
        });

    $app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}/{reviewer}',
        function (Request $request, Response $response, array $args) use ($app) {
            return $app->helper->review_route($args, $this, $response, true);
        });

    $app->get('/overview',
        function (Request $request, Response $response, array $args) use ($app) {
            $app->helper->overview_route($args, $this, $response);
        });

    $app->get('/todo',
        function (Request $request, Response $response, array $args) use ($app) {
            $app->helper->todo_route($args, $this, $response);
        });
});

$app->group('/api', function () use ($app) {

    $app->post('/upload/[{experiment:ex[1-3]}]',
        function (Request $request, Response $response, array $args) use ($app) {
            $experiment = $args['experiment'];
            $run = decodeJsonBody($request);
            if (!$run) {
                return error_response($response, $this->logger, 400, "empty: " . print_r($request->getBody(), true));
            }
            $detector = $run->{'detector'};
            if (!$detector) {
                return error_response($response, $this->logger, 400, "no detector: " . print_r($run, true));
            }
            $project = $run->{'project'};
            if (!$project) {
                return error_response($response, $this->logger, 400, "no project: " . print_r($run, true));
            }
            $version = $run->{'version'};
            if (!$version) {
                return error_response($response, $this->logger, 400, "no version: " . print_r($run, true));
            }
            $hits = $run->{'potential_hits'};
            $this->logger->info("received data for '" . $experiment . "', '" . $project . "." . $version . "' with " . count($hits) . " potential hits.");

            $uploader = new FindingsUploader($app->db, $this->logger);
            $uploader->processData($experiment, $run, $hits);
            $files = $request->getUploadedFiles();
            $this->logger->info("received " . count($files) . " files");
            if ($files) {
                foreach ($files as $img) {
                    $app->dir->handleImage($experiment, $detector, $project, $version, $img);
                }
            }
            return $response->withStatus(200);
        });

    $app->post('/upload/metadata',
        function (Request $request, Response $response, array $args) use ($app) {
            $obj = decodeJsonBody($request);
            if (!$obj) {
                return error_response($response, $this->logger, 400, "empty: " . print_r($request->getBody(), true));
            }
            $uploader = new MetadataUploader($app->db, $this->logger);
            foreach ($obj as $o) {
                $uploader->processMetaData($o);
            }
            return $response->withStatus(200);
        });

});
