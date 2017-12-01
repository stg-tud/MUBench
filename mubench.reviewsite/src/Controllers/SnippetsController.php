<?php

namespace MuBench\ReviewSite\Controllers;


use MuBench\ReviewSite\Models\Snippet;
use Slim\Http\Request;
use Slim\Http\Response;

class SnippetsController extends Controller
{

    public function postSnippet(Request $request, Response $response, array $args)
    {
        $form = $request->getParsedBody();
        $projectId = $args['project_muid'];
        $versionId = $args['version_muid'];
        $misuseId = $args['misuse_muid'];
        $code = $form['snippet'];
        $line = $form['line'];
        self::createSnippet($projectId, $versionId, $misuseId, $code, $line);
        return $response->withRedirect("{$this->site_base_url}{$form['path']}");
    }

    public function deleteSnippet(Request $request, Response $response, array $args)
    {
        $form = $request->getParsedBody();
        $snippetId = $args['snippet_id'];

        Snippet::find($snippetId)->delete();

        return $response->withRedirect("{$this->site_base_url}{$form['path']}");
    }

    static function createSnippet($projectId, $versionId, $misuseId, $code, $line)
    {
        $snippet = Snippet::firstOrNew(['misuse_muid' => $misuseId, 'project_muid' => $projectId, 'version_muid' => $versionId, 'line' => $line]);
        $snippet->snippet = $code;
        $snippet->save();
    }
}
