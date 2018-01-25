<?php

namespace MuBench\ReviewSite\Controllers;


use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Tag;
use Slim\Http\Request;
use Slim\Http\Response;

class TagsController extends Controller
{
    public function postTag(Request $request, Response $response, array $args)
    {
        $formData = $request->getParsedBody();
        $tag_id = $formData['tag_name'];
        $misuse_id = $formData['misuse_id'];

        $this->addTagToMisuse($misuse_id, $tag_id);

        return $response->withRedirect("{$this->settings['site_base_url']}{$formData['path']}");
    }

    public function deleteTag(Request $request, Response $response, array $args)
    {
        $formData = $request->getParsedBody();
        $tag_id = $args['tag_id'];
        $misuse_id = $formData['misuse_id'];

        $this->deleteTagFromMisuse($misuse_id, $tag_id);

        return $response->withRedirect("{$this->settings['site_base_url']}{$formData['path']}");
    }

    public function getTags(Request $request, Response $response, array $args)
    {
        $tags = Tag::all();
        $results = array(1 => array(), 2 => array(), 3 => array());
        $totals = array(1 => array(), 2 => array(), 3 => array());
        foreach($tags as $tag){
            $tagged_misuses = $tag->misuses;
            foreach($tagged_misuses as $misuse){
                $results[$misuse->run->experiment_id][$misuse->detector->muid][$tag->name][] = $misuse;
                $totals[$misuse->run->experiment_id][$tag->name][] = $misuse;
            }
        }
        foreach($totals as $key => $total){
            $results[$key]["total"] = $total;
        }
        return $this->renderer->render($response, 'tag_stats.phtml',
            ['results' => $results, 'tags' => $tags]);
    }

    function addTagToMisuse($misuseId, $tagName)
    {
        $tag = Tag::firstOrCreate(['name' => $tagName]);
        Misuse::find($misuseId)->misuse_tags()->syncWithoutDetaching($tag->id);
    }

    function deleteTagFromMisuse($misuseId, $tagId)
    {
        Misuse::find($misuseId)->misuse_tags()->detach($tagId);
    }
}
