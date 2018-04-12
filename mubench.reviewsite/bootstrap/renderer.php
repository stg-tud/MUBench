<?php

use MuBench\ReviewSite\Models\Reviewer;
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

    $blind_mode = $container->settings['blind_mode']['enabled'];

    $detectorName = function($detector_name) use ($container, $blind_mode) {
        if($blind_mode && array_key_exists($detector_name, $container->settings['blind_mode']['detector_blind_names'])){
            return $container->settings['blind_mode']['detector_blind_names'][$detector_name];
        }
        return $detector_name;
    };

    $reviewerName = function($reviewer)  use ($blind_mode) {
        if($blind_mode){
            return "reviewer-" . $reviewer->id;
        }
        return $reviewer->name;
    };

    $detectorPathId = function($detector) use ($blind_mode) {
        if($blind_mode){
            return $detector->id;
        }
        return $detector->muid;
    };

    $reviewerPathId = function($reviewer) use ($blind_mode) {
        if($blind_mode){
            return $reviewer->id;
        }
        return $reviewer->name;
    };

    $markdown_parser = new Parsedown();
    $markdown_parser->setBreaksEnabled(True);

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
        'detectorName' => $detectorName,
        'reviewerName' => $reviewerName,
        'detectorPathId' => $detectorPathId,
        'reviewerPathId' => $reviewerPathId
    ];

    return new PhpRenderer(__DIR__ . '/../templates/', $defaultTemplateVariables);
};
