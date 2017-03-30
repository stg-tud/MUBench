<?php
/** @var \Slim\App $app */

use MuBench\ReviewSite\Controller\FindingsUploader;
use MuBench\ReviewSite\Controller\MetadataUploader;
use MuBench\ReviewSite\Controller\ReviewUploader;
use MuBench\ReviewSite\Controller\SnippetUploader;
use MuBench\ReviewSite\DBConnection;
use MuBench\ReviewSite\DirectoryHelper;
use MuBench\ReviewSite\Model\Experiment;
use MuBench\ReviewSite\RoutesHelper;
use Slim\Http\Request;
use Slim\Http\Response;

require_once "route_utils.php";

$logger = $app->getContainer()['logger'];
$database = $app->getContainer()['database'];
$renderer = $app->getContainer()['renderer'];
// TODO rename RoutesHelper to ResultsViewController
$routesHelper = new RoutesHelper($database, $renderer, $logger, $settings['upload'], $settings['site_base_url']);

$app->get('/', [$routesHelper, 'index']);
$app->get('/{exp:ex[1-3]}/{detector}', [$routesHelper, 'detector']);
$app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}', [$routesHelper, 'review']);
$app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}/{reviewer}', [$routesHelper, 'review']);
$app->get('/stats', [$routesHelper, 'stats']);

$app->group('/private', function () use ($app, $routesHelper, $database) {
    $app->get('/', [$routesHelper, 'index']);
    $app->get('/{exp:ex[1-3]}/{detector}', [$routesHelper, 'detector']);
    $app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}', [$routesHelper, 'review']);
    $app->get('/{exp:ex[1-3]}/{detector}/{project}/{version}/{misuse}/{reviewer}', [$routesHelper, 'review']);
    $app->get('/stats', [$routesHelper, 'stats']);
    $app->get('/overview', [$routesHelper, 'overview']);
    $app->get('/todo', [$routesHelper, 'todos']);
});

$app->group('/api/upload', function () use ($app, $settings, $database) {
    $app->post('/[{experiment:ex[1-3]}]',
        function (Request $request, Response $response, array $args) use ($settings, $database) {
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

            $uploader = new FindingsUploader($database, $this->logger);
            $uploader->processData($experiment, $run);
            $files = $request->getUploadedFiles();
            $this->logger->info("received " . count($files) . " files");
            if ($files) {
                $directoryHelper = new DirectoryHelper($settings['upload'], $this->logger);
                foreach ($files as $img) {
                    $directoryHelper->handleImage($experiment, $detector, $project, $version, $img);
                }
            }
            return $response->withStatus(200);
        });

    $app->post('/metadata',
        function (Request $request, Response $response, array $args) use ($database) {
            $obj = decodeJsonBody($request);
            if (!$obj) {
                return error_response($response, $this->logger, 400, "empty: " . print_r($request->getBody(), true));
            }
            $uploader = new MetadataUploader($database, $this->logger);
            foreach ($obj as $o) {
                $uploader->processMetaData($o);
            }
            return $response->withStatus(200);
        });

    $app->post('/review/{exp:ex[1-3]}/{detector}',
        function (Request $request, Response $response, array $args) use ($database, $settings) {
            $obj = $request->getParsedBody();
            $uploader = new ReviewUploader($database, $this->logger);
            $uploader->processReview($obj);
            $site_base_url = $settings['site_base_url'];
            if (strcmp($obj["origin"], "") !== 0) {
                return $response->withRedirect("{$site_base_url}index.php/{$obj["origin"]}");
            } else {
                return $response->withRedirect("{$site_base_url}index.php/private/{$args['exp']}/{$args['detector']}");
            }
        });

    $app->post('/snippet',
        function (Request $request, Response $response, array $args) use ($database, $settings) {
            $obj = $request->getParsedBody();
            $uploader = new SnippetUploader($database, $this->logger);
            $uploader->processSnippet($obj);
            return $response->withRedirect("{$settings['site_base_url']}index.php/{$obj['path']}");
        });
});
