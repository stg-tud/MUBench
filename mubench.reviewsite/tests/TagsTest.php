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
        $this->db->table('tags')->insert(['name' => 'test1']);
        $this->db->table('tags')->insert(['name' => 'test2']);
        $this->db->table('tags')->insert(['name' => 'test3']);
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

    function test_save_misuse_tags()
    {
        $misuse_tag1 = [
            "tag" => 'test1',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $misuse_tag2 = [
            "tag" => 'test2',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $this->tagController->saveTagForMisuse($misuse_tag2);
        $expected_tags = [
            ['id' => 1, 'name' => 'test1'],
            ['id' => 2, 'name' => 'test2']
        ];
        $misuse_tags = $this->db->getTagsForMisuse(1, 1, "-project-", "-version-", "-misuse-");

        self::assertEquals($expected_tags, $misuse_tags);
    }

    function test_delete_misuse_tag()
    {
        $misuse_tag1 = [
            "tag" => 'test1',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $misuse_tag2 = [
            "tag" => 'test2',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $remove_tag = [
            "tag" => 1,
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $expected_tags = [
            ['id' => 2, 'name' => 'test2']
        ];
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $this->tagController->saveTagForMisuse($misuse_tag2);
        $this->tagController->deleteMisuseTag($remove_tag);
        $misuse_tags = $this->db->getTagsForMisuse(1, 1, "-project-", "-version-", "-misuse-");

        self::assertEquals($expected_tags, $misuse_tags);
    }

    function test_adding_same_tag_twice()
    {
        $misuse_tag1 = [
            "tag" => 'test1',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $misuse_tag2 = [
            "tag" => 'test2',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];

        $expected_tags = [
            ['id' => 1, 'name' => 'test1'],
            ['id' => 2, 'name' => 'test2']
        ];
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $this->tagController->saveTagForMisuse($misuse_tag2);
        $misuse_tags = $this->db->getTagsForMisuse(1, 1, "-project-", "-version-", "-misuse-");

        self::assertEquals($expected_tags, $misuse_tags);
    }
}
