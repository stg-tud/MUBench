<?php

use MuBench\ReviewSite\ViewExtensions\AnonymousViewExtension;
use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\ReviewState;
use Slim\Views\PhpRenderer;

$container['renderer'] = function ($container) {
    /** @var \Slim\Http\Request $request */
    $request = $container->request;
    $user = $container->user;

    $siteBaseURL = rtrim(str_replace('index.php', '', $request->getUri()->getBasePath()), '/') . '/';
    $publicURLPrefix = $siteBaseURL;
    $privateURLPrefix = $siteBaseURL . 'private/';
    $urlPrefix = $user ? $privateURLPrefix : $publicURLPrefix;

    $path = $request->getUri()->getPath();
    if ($path && $path[0] === '/') {
        $path = substr($path, 1);
    }

    $experiments = \MuBench\ReviewSite\Models\Experiment::all();
    $detectors = [];
    foreach ($experiments as $experiment) { /** @var \MuBench\ReviewSite\Models\Experiment $experiment */
        $detectors[$experiment->id] = \MuBench\ReviewSite\Models\Detector::withRuns($experiment);
    }

    $pathFor = function ($routeName, $args = [], $private = false) use ($container, $user) {
        $routeName = $user || $private ? "private.$routeName" : $routeName;
        return $container->router->pathFor($routeName, $args);
    };

    $anonymousViewExtension = new AnonymousViewExtension($container);

    $markdown_parser = new Parsedown();
    $markdown_parser->setBreaksEnabled(True);
    $exp_det_reviewstate = [];
    foreach($experiments as $experiment){
        $exp_det_reviewstate[$experiment->id] = [];
        foreach($detectors[$experiment->id] as $detector){
            $review_states = [ReviewState::NEEDS_REVIEW => false, ReviewState::NEEDS_CLARIFICATION => false, ReviewState::DISAGREEMENT => false];
            $runs = RunsController::getRuns($detector, $experiment, $request->getQueryParam("ex2_review_size", $container->settings["default_ex2_review_size"]));
            $found_all_reviewstates = false;
            foreach ($runs as $run) {
                foreach ($run->misuses as $misuse) {
                    /** @var Misuse $misuse */
                    if($misuse->getReviewState() == ReviewState::NEEDS_REVIEW || $misuse->getReviewState() == ReviewState::NEEDS_CLARIFICATION || $misuse->getReviewState() == ReviewState::DISAGREEMENT) {
                        $review_states[$misuse->getReviewState()] = True;
                        if($review_states[ReviewState::NEEDS_REVIEW] && $review_states[ReviewState::NEEDS_CLARIFICATION] && $review_states[ReviewState::DISAGREEMENT]){
                            $found_all_reviewstates = true;
                            break;
                        }
                    }
                }
                if($found_all_reviewstates){
                    break;
                }
            }
            $exp_det_reviewstate[$experiment->id][$detector->id] = $review_states;
        }
    }

    $defaultTemplateVariables = [
        'user' => $user,

        'pathFor' => $pathFor,
        'isCurrentPath' => function ($routeName, $args = []) use ($container, $pathFor) {
            $path = $container->request->getUri()->getPath();
            $checkPath = $pathFor($routeName, $args);
            return strpos($path, $checkPath) !== false;
        },
        'srcUrlFor' => function ($resourceName) use ($container, $siteBaseURL) {
            return  "$siteBaseURL$resourceName";
        },
        'loginPath' => $privateURLPrefix . $path,

        'site_base_url' => $siteBaseURL,
        'public_url_prefix' => $publicURLPrefix,
        'private_url_prefix' => $privateURLPrefix,
        'url_prefix' => $urlPrefix,
        'uploads_url_prefix' => $publicURLPrefix . $container->settings['upload'],
        'uploads_path' => $container->settings['upload'],

        'path' => $publicURLPrefix . $path,
        'origin_param' => htmlspecialchars("?origin=$publicURLPrefix$path"),
        'origin_path' => htmlspecialchars($request->getQueryParam('origin', '')),

        'experiments' => $experiments,
        'experiment' => null,
        'detectors' => $detectors,
        'detector' => null,
        'resolution_reviewer' => Reviewer::where('name' ,'resolution')->first(),

        'ex2_review_size' => $request->getQueryParam("ex2_review_size", $container->settings["default_ex2_review_size"]),

        'markdown_parser' => $markdown_parser,
        'exp_det_reviewstate' => $exp_det_reviewstate,
        'detectorName' => array($anonymousViewExtension, "getDetectorName"),
        'reviewerName' => array($anonymousViewExtension, "getReviewerName"),
        'detectorPathId' => array($anonymousViewExtension,"getDetectorPathId"),
        'reviewerPathId' => array($anonymousViewExtension, "getReviewerPathId")
    ];

    return new PhpRenderer(__DIR__ . '/../templates/', $defaultTemplateVariables);
};
