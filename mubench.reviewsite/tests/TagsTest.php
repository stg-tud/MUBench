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
    }

    function test_get_all_tags()
    {
        $this->db->table('tags')->insert(['name' => 'test1']);
        $tags = $this->db->getAllTags();
        $expected_tags = [
            ['id' => 1, 'name' => 'test1']
        ];
        self::assertEquals($expected_tags, $tags);
    }

    function test_save_misuse_tags()
    {
        $this->db->table('tags')->insert(['name' => 'test1']);
        $misuse_tag1 = [
            "tag" => 'test1',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $expected_tags = [
            ['id' => 1, 'name' => 'test1']
        ];
        $misuse_tags = $this->db->getTagsForMisuse(1, 1, "-project-", "-version-", "-misuse-");

        self::assertEquals($expected_tags, $misuse_tags);
    }

    function test_delete_misuse_tag()
    {
        $this->db->table('tags')->insert(['name' => 'test1']);
        $misuse_tag1 = [
            "tag" => 'test1',
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
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $this->tagController->deleteMisuseTag($remove_tag);
        $misuse_tags = $this->db->getTagsForMisuse(1, 1, "-project-", "-version-", "-misuse-");

        self::assertEquals([], $misuse_tags);
    }

    function test_adding_same_tag_twice()
    {
        $this->db->table('tags')->insert(['name' => 'test1']);
        $misuse_tag1 = [
            "tag" => 'test1',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $expected_tags = [
            ['id' => 1, 'name' => 'test1']
        ];
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $misuse_tags = $this->db->getTagsForMisuse(1, 1, "-project-", "-version-", "-misuse-");

        self::assertEquals($expected_tags, $misuse_tags);
    }

    function test_add_unknown_tag()
    {
        $misuse_tag1 = [
            "tag" => 'unknown_tag',
            "exp" => 1,
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ];
        $expected_tags = [
            ['id' => 1, 'name' => 'unknown_tag']
        ];
        $this->tagController->saveTagForMisuse($misuse_tag1);
        $misuse_tags = $this->db->getTagsForMisuse(1, 1, "-project-", "-version-", "-misuse-");

        self::assertEquals($expected_tags, $misuse_tags);
    }
}
