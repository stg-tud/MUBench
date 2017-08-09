<?php

require_once "DatabaseTestCase.php";

use MuBench\ReviewSite\Controller\TagController;

class TagTest extends DatabaseTestCase
{

    private $tagController;

    function setUp()
    {
        parent::setUp();
        $this->tagController = new TagController($this->db, $this->logger);
        $this->tagController->saveNewTag("test1");
        $this->tagController->saveNewTag("test2");
        $this->tagController->saveNewTag("test3");
    }

    function test_get_all_tags()
    {
        $tags = $this->db->getAllTags();
        $expected_tags = [
            ['id' => 1, 'name' => 'test1'],
            ['id' => 2, 'name' => 'test2'],
            ['id' => 3, 'name' => 'test3']
        ];
        self::assertEquals($expected_tags, $tags);
    }

    function test_save_new_tag()
    {
        $this->tagController->saveNewTag("test");
        $tags = $this->db->getAllTags();

        $expected_tags = [
            ['id' => 1, 'name' => 'test1'],
            ['id' => 2, 'name' => 'test2'],
            ['id' => 3, 'name' => 'test3'],
            ['id' => 4, 'name' => 'test']
        ];
        self::assertEquals($expected_tags, $tags);
    }

    function test_save_misuse_tags()
    {
        $tag = [
            "name" => 'test1',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "finding" => "-finding-"
        ];
        $this->tagController->saveTagForMisuse($tag);
        $expected_tags = [
            ['id' => 1, 'name' => 'test1']
        ];
        $misuse_tags = $this->db->getTagsForMisuse(1, 1, "-project-", "-version-", "-finding-");
        self::assertEquals($expected_tags, $misuse_tags);
    }


}
