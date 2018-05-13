<?php

namespace MuBench\ReviewSite\Controllers;

require_once "SlimTestCase.php";

use DatabaseTestCase;
use MuBench\ReviewSite\Models\Misuse;
use MuBench\ReviewSite\Models\Tag;
use SlimTestCase;

class TagControllerTest extends SlimTestCase
{
    /** @var TagsController */
    private $tagController;

    /** @var  Misuse */
    private $misuse;

    function setUp()
    {
        parent::setUp();
        $this->tagController = new TagsController($this->container);
        $misuse = new Misuse;
        $misuse->metadata_id = 1;
        $misuse->misuse_muid = '1';
        $misuse->run_id = 1;
        $misuse->detector_id = 42;
        $misuse->save();
    }

    function test_save_misuse_tags()
    {
        $this->tagController->addTagToMisuse(1, 'test-dataset', 1);

        $misuseTags = Misuse::find(1)->misuse_tags;

        self::assertEquals('test-dataset', $misuseTags->first()->name);
        self::assertEquals(1, $misuseTags->first()->pivot->reviewer_id);
    }

    function test_delete_misuse_tag()
    {
        $this->tagController->addTagToMisuse(1, 'test-dataset', 1);
        $this->tagController->addTagToMisuse(1, 'test-dataset', 2);
        $this->tagController->deleteTagFromMisuse(1, 2, 2);

        $misuseTags = Misuse::find(1)->misuse_tags;

        self::assertEquals(1, $misuseTags->count());
        self::assertEquals('test-dataset', $misuseTags->first()->name);
        self::assertEquals(1, $misuseTags->first()->pivot->reviewer_id);
    }

    function test_adding_same_tag_twice()
    {
        $this->tagController->addTagToMisuse(1, 'test-tag', 1);
        $this->tagController->addTagToMisuse(1, 'test-tag', 1);

        $misuseTags = Misuse::find(1)->misuse_tags;

        self::assertEquals(1, count($misuseTags));
    }

    function test_add_unknown_tag()
    {
        $this->tagController->addTagToMisuse(1, 'test-tag', 1);

        $misuseTags = Misuse::find(1)->misuse_tags;

        self::assertEquals('test-tag', $misuseTags->get(0)->name);
    }

    function test_update_tag()
    {
        $this->tagController->addTagToMisuse(1, 'test-tag', 1);

        $tag = Tag::where('name', 'test-tag')->first();
        $tag_id = $tag->id;
        $this->tagController->updateTag($tag->id, ['name' => 'new-name', 'color' => '#555555']);

        $updatedTag = Tag::find($tag_id);

        self::assertEquals('new-name', $updatedTag->name);
        self::assertEquals('#555555', $updatedTag->color);
    }

    function test_delete_tag()
    {
        $this->tagController->addTagToMisuse(1, 'test-tag', 1);
        $tag_id = Tag::where('name', 'test-tag')->first()->id;


        $this->tagController->deleteTagAndRemoveFromMisuses($tag_id);
        self::assertEmpty(Misuse::find(1)->misuse_tags);
        self::assertNull(Tag::find($tag_id));
    }
}
