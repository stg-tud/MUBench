<?php

namespace MuBench\ReviewSite\Controllers;

require_once "SlimTestCase.php";

use DatabaseTestCase;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Review;
use MuBench\ReviewSite\Models\Reviewer;
use MuBench\ReviewSite\Models\Tag;
use SlimTestCase;

class TagControllerTest extends SlimTestCase
{
    /** @var TagsController */
    private $tagController;

    /** @var  Misuse */
    private $review;

    function setUp()
    {
        parent::setUp();
        $reviewer = Reviewer::create(['name' => 'reviewer']);
        $misuse = new Misuse;
        $misuse->metadata_id = 1;
        $misuse->misuse_muid = '1';
        $misuse->run_id = 1;
        $misuse->detector_id = 42;
        $misuse->save();
        $this->createReview($misuse, $reviewer, 'Yes');
        $this->review = Review::find(1);
        $this->tagController = new TagsController($this->container);
    }

    function test_save_review_tags()
    {
        TagsController::syncReviewTags($this->review->id, ['test-dataset']);

        $reviewTags = $this->review->tags;

        self::assertEquals('test-dataset', $reviewTags->first()->name);
    }

    function test_delete_review_tag()
    {
        TagsController::syncReviewTags($this->review->id, ['test-dataset', 'test-dataset2']);
        TagsController::deleteTagFromReview($this->review->id, 1);

        $reviewTags = $this->review->tags;

        self::assertEquals(1, $reviewTags->count());
        self::assertEquals('test-dataset2', $reviewTags->first()->name);
    }

    function test_adding_same_tag_twice()
    {
        TagsController::syncReviewTags($this->review->id, ['test-tag']);
        TagsController::syncReviewTags($this->review->id, ['test-tag']);

        self::assertEquals(1, $this->review->tags->count());
    }

    function test_add_unknown_tag()
    {
        TagsController::syncReviewTags($this->review->id, ['test-tag']);

        self::assertEquals('test-tag', $this->review->tags[0]->name);
    }

    function test_update_tag()
    {
        TagsController::syncReviewTags($this->review->id, ['test-tag']);

        $tag = Tag::where('name', 'test-tag')->first();
        $tag_id = $tag->id;
        $this->tagController->updateTag($tag->id, ['name' => 'new-name', 'color' => '#555555']);

        $updatedTag = Tag::find($tag_id);

        self::assertEquals('new-name', $updatedTag->name);
        self::assertEquals('#555555', $updatedTag->color);
    }

    function test_delete_tag()
    {
        TagsController::syncReviewTags($this->review->id, ['test-tag']);
        $tag_id = Tag::where('name', 'test-tag')->first()->id;


        $this->tagController->deleteTagAndRemoveFromReviews($tag_id);
        self::assertEmpty($this->review->tags);
        self::assertNull(Tag::find($tag_id));
    }
}
