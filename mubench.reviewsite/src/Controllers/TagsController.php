<?php

namespace MuBench\ReviewSite\Controllers;


use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\Tag;
use Slim\Http\Request;
use Slim\Http\Response;

class TagsController extends Controller
{

    public function manageTags(Request $request, Response $response, array $args)
    {
        return $this->renderer->render($response, 'manage_tags.phtml', ['tags' => Tag::all()]);
    }

    public function updateTags(Request $request, Response $response, array $args)
    {
        $formData = $request->getParsedBody();
        $tags = $formData['tags'];
        foreach ($tags as $key => $t) {
            $this->updateTag($key, $t);
        }
        return $response->withRedirect($this->router->pathFor('private.tags.manage'));
    }

    public function deleteTag(Request $request, Response $response, array $args)
    {
        $tag_id = $args['tag_id'];
        $this->deleteTagAndRemoveFromReviews($tag_id);
        return $response->withRedirect($this->router->pathFor('private.tags.manage'));
    }

    public function getTags(Request $request, Response $response, array $args)
    {
        // TODO: fix tag statistics with reviews
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

    public function updateTag($id, $tagInfo){
        $tag = Tag::find($id);
        $tag->name = $tagInfo['name'];
        $tag->color = $tagInfo['color'];
        $tag->save();
    }

    function deleteTagAndRemoveFromReviews($tag_id)
    {
        $tag = Tag::find($tag_id);
        /** @var Review $review */
        foreach($tag->reviews as $review){
            $review->tags()->detach($tag_id);
        }
        $tag->delete();
    }

    static function syncReviewTags($reviewId, $tagNames)
    {
        $tagIds = [];
        foreach($tagNames as $tagName){
            $tag = Tag::where('name', $tagName)->first();
            if(!$tag){
                $tag = new Tag();
                $tag->name = $tagName;
                $tag->color = '#808080';
                $tag->save();
            }
            $tagIds[] = $tag->id;
        }
        Review::find($reviewId)->tags()->sync($tagIds);
    }

    static function deleteTagFromReview($reviewId, $tagId)
    {
        Review::find($reviewId)->tags()->detach($tagId);
    }
}
