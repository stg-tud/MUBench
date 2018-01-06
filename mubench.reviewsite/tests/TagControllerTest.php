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
        $this->tagController->addTagToMisuse(1, 'test-dataset');

        $misuseTags = Misuse::find(1)->misuse_tags;

        self::assertEquals('test-dataset', $misuseTags->get(0)->name);
    }

    function test_delete_misuse_tag()
    {
        $this->tagController->deleteTagFromMisuse(1, 2);

        $misuseTags = Misuse::find(1)->misuse_tags;

        self::assertEmpty($misuseTags);
    }

    function test_adding_same_tag_twice()
    {
        $this->tagController->addTagToMisuse(1, 'test-tag');
        $this->tagController->addTagToMisuse(1, 'test-tag');

        $misuseTags = Misuse::find(1)->misuse_tags;

        self::assertEquals(1, count($misuseTags));
    }

    function test_add_unknown_tag()
    {
        $this->tagController->addTagToMisuse(1, 'test-tag');

        $misuseTags = Misuse::find(1)->misuse_tags;

        self::assertEquals('test-tag', $misuseTags->get(0)->name);
    }

    function update_tag()
    {
        $this->tagController->addTagToMisuse(1, 'test-tag');

        $misuseTags = Misuse::find(1)->misuse_tags;
        $tag = Tag::where('name', 'test-tag')->first();
        $this->tagController->updateTag($tag->id, ['name' => 'new-name', 'color' => '#555555']);

        $updatedTag = Tag::where('name', 'test-tag')->first();

        self::assertEquals('new-name', $updatedTag->name);
        self::assertEquals('#555555', $updatedTag->color);
    }
}
