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
        return $response->withRedirect($this->router->pathFor('private.view', $args));
    }

    public function manageTags(Request $request, Response $response, array $args)
    {
        return $this->renderer->render($response, 'manage_tags.phtml', ['tags' => Tag::all()]);
    }

    public function updateTags(Request $request, Response $response, array $args)
    {
        $formData = $request->getParsedBody();
        $tags = $formData['tags'];
        foreach ($tags as $key => $t) {
            $tag = Tag::find($key);
            $tag->name = $t['name'];
            $tag->color = $t['color'];
            $tag->save();
        }
        return $response->withRedirect($this->router->pathFor('private.tags.manage'));
    }

    public function deleteTags(Request $request, Response $response, array $args)
    {
        $tag_id = $args['tag_id'];
        Tag::find($tag_id)->delete();
        return $response->withRedirect($this->router->pathFor('private.tags.manage'));
    }

    public function deleteTag(Request $request, Response $response, array $args)
    {
        $formData = $request->getParsedBody();
        $tag_id = $args['tag_id'];
        $misuse_id = $formData['misuse_id'];

        $this->deleteTagFromMisuse($misuse_id, $tag_id);

        return $response->withRedirect($this->router->pathFor('private.view', $args));
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
        $tag = Tag::where('name', $tagName)->first();
        if(!$tag){
            $tag = new Tag();
            $tag->name = $tagName;
            $tag->color = '#808080';
            $tag->save();
        }
        Misuse::find($misuseId)->misuse_tags()->syncWithoutDetaching($tag->id);
    }

    function deleteTagFromMisuse($misuseId, $tagId)
    {
        Misuse::find($misuseId)->misuse_tags()->detach($tagId);
    }
}
