<?php
/** @var \Slim\App $app */

use MuBench\ReviewSite\Controllers\DownloadController;
use MuBench\ReviewSite\Controllers\FindingsController;
use MuBench\ReviewSite\Controllers\FindingsUploader;
use MuBench\ReviewSite\Controllers\MisuseTagsController;
use MuBench\ReviewSite\Controllers\SnippetUploader;
use MuBench\ReviewSite\DirectoryHelper;
use MuBench\ReviewSite\RoutesHelper;

$app->get('/', \MuBench\ReviewSite\Controllers\ExperimentsController::class.":index")->setName('/');
$app->group('/experiments/{experiment_id}', function() use ($app) {
    $app->group('/detectors/{detector_muid}', function () use ($app) {
        $app->get('/runs', \MuBench\ReviewSite\Controllers\RunsController::class . ":getIndex")->setName('experiment.detector');
        $app->get('/runs.csv', \MuBench\ReviewSite\Controllers\RunsController::class . ":downloadRuns")->setName('download.runs');
        $app->group('/projects/{project_muid}/versions/{version_muid}/misuses/{misuse_muid}', function() use ($app) {
            $app->get('', \MuBench\ReviewSite\Controllers\ReviewsController::class . ":getReview")->setName('view');
            $app->get('/reviewers/{reviewer_name}', \MuBench\ReviewSite\Controllers\ReviewsController::class . ":getReview")->setName('review');
        });
    });
    $app->get('/results.csv', \MuBench\ReviewSite\Controllers\RunsController::class . ":downloadResults")->setName('stats.results.csv');
});
$app->get('/results', \MuBench\ReviewSite\Controllers\RunsController::class.":getResults")->setName('stats.results');
$app->get('/tags', \MuBench\ReviewSite\Controllers\TagsController::class.":getTags")->setName('stats.tags');
$app->get('/violations', \MuBench\ReviewSite\Controllers\ViolationsController::class.":getViolations")->setName('stats.violations');


$app->group('/private', function () use ($app) {
    $app->get('/', \MuBench\ReviewSite\Controllers\ExperimentsController::class.":index")->setName('private./');
    $app->get('/import', \MuBench\ReviewSite\Controllers\RunsController::class.":import")->setName('private.import');
    $app->get('/runs/manage', \MuBench\ReviewSite\Controllers\RunsController::class.":manageRuns")->setName('private.manage.runs');
    $app->group('/experiments/{experiment_id}', function() use ($app) {
        $app->group('/detectors/{detector_muid}', function() use ($app) {
            $app->post('/import', \MuBench\ReviewSite\Controllers\RunsController::class.":import_runs")->setName('private.import.detector');
            $app->get('/runs', \MuBench\ReviewSite\Controllers\RunsController::class . ":getIndex")->setName('private.experiment.detector');
            $app->get('/runs.csv', \MuBench\ReviewSite\Controllers\RunsController::class . ":downloadRuns")->setName('private.download.runs');
            $app->group('/projects/{project_muid}/versions/{version_muid}/misuses/{misuse_muid}', function() use ($app) {
                $app->get('', \MuBench\ReviewSite\Controllers\ReviewsController::class . ":getReview")->setName('private.view');
                $app->get('/reviewers/{reviewer_name}', \MuBench\ReviewSite\Controllers\ReviewsController::class . ":getReview")->setName('private.review');
            });
        });
        $app->get('/reviews/{reviewer_name}/open', \MuBench\ReviewSite\Controllers\ReviewsController::class . ":getTodo")->setName('private.todo');
        $app->get('/reviews/{reviewer_name}/closed', \MuBench\ReviewSite\Controllers\ReviewsController::class . ":getOverview")->setName('private.overview');
        $app->get('/results.csv', \MuBench\ReviewSite\Controllers\RunsController::class.":downloadResults")->setName('private.stats.results.csv');
    });
    $app->get('/results', \MuBench\ReviewSite\Controllers\RunsController::class.":getResults")->setName('private.stats.results');
    $app->get('/tags', \MuBench\ReviewSite\Controllers\TagsController::class.":getTags")->setName('private.stats.tags');
    $app->get('/tags/manage', \MuBench\ReviewSite\Controllers\TagsController::class.":manageTags")->setName('private.tags.manage');
    $app->get('/violations', \MuBench\ReviewSite\Controllers\ViolationsController::class.":getViolations")->setName('private.stats.violations');
})->add(new \MuBench\ReviewSite\Middleware\AuthMiddleware($container));

$app->group('', function () use ($app, $settings) {
    $app->post('/metadata', \MuBench\ReviewSite\Controllers\MetadataController::class.":putMetadata");
    $app->post('/tags/rename', \MuBench\ReviewSite\Controllers\TagsController::class.":updateTags")->setName('private.tags.update');
    $app->get('/tags/{tag_id}/delete', \MuBench\ReviewSite\Controllers\TagsController::class.":deleteTag")->setName('private.tags.delete');
    $app->post('/runs/delete', \MuBench\ReviewSite\Controllers\RunsController::class.":deleteRuns")->setName('private.runs.massDelete');
    $app->group('/experiments/{experiment_id}/detectors/{detector_muid}/projects/{project_muid}/versions/{version_muid}', function() use ($app) {
        $app->post('/runs', \MuBench\ReviewSite\Controllers\RunsController::class.":postRun");
        $app->post('/runs/delete', MuBench\ReviewSite\Controllers\RunsController::class.":deleteRun")->setName('private.runs.delete');
        $app->group('/misuses/{misuse_muid}', function() use ($app) {
            $app->post('/tags', \MuBench\ReviewSite\Controllers\TagsController::class . ":postTag")->setName('private.tag.add');
            $app->post('/tags/{tag_id}/delete', \MuBench\ReviewSite\Controllers\TagsController::class . ":removeTag")->setName('private.tag.remove');
            $app->post('/reviews/{reviewer_name}', \MuBench\ReviewSite\Controllers\ReviewsController::class . ":postReview")->setName('private.update.review');
            $app->post('/snippets', \MuBench\ReviewSite\Controllers\SnippetsController::class . ":postSnippet")->setName('private.snippet.add');
            $app->post('/snippets/{snippet_id}/delete', \MuBench\ReviewSite\Controllers\SnippetsController::class . ":deleteSnippet")->setName('private.snippet.remove');
        });
    });
})->add(new \MuBench\ReviewSite\Middleware\AuthMiddleware($container));
