<?php

namespace MuBench\ReviewSite\Controllers;


use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Snippet;
use Slim\Http\Request;
use Slim\Http\Response;

class SnippetsController extends Controller
{

    public function postSnippet(Request $request, Response $response, array $args)
    {
        $form = $request->getParsedBody();
        $detectorId = $args['detector_muid'];
        $projectId = $args['project_muid'];
        $versionId = $args['version_muid'];
        $misuseId = $args['misuse_muid'];
        $code = $form['snippet'];
        $line = $form['line'];
        $misuse = Misuse::find($form['misuse_id']);
        Snippet::createIfNotExists($projectId, $versionId, $misuseId, $misuse->getFile(), $line, $code, $detectorId);
        return $response->withRedirect($form['path']);
    }

    public function deleteSnippet(Request $request, Response $response, array $args)
    {
        $form = $request->getParsedBody();
        $snippetId = $args['snippet_id'];

        Snippet::find($snippetId)->delete();

        return $response->withRedirect($form['path']);
    }

}
