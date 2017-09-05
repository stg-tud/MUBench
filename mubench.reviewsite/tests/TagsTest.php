<?php

namespace MuBench\ReviewSite\Controller;

use DatabaseTestCase;

class TagTest extends DatabaseTestCase
{
    /** @var TagController */
    private $tagController;

    function setUp()
    {
        parent::setUp();
        $this->tagController = new TagController($this->db, $this->logger, "-site-base-url-");
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
        $this->tagController->addTag('ex1', 1, '-project-', '-version-', '-misuse-', 'test1');
        $misuseTags = $this->db->getTagsForMisuse('ex1', 1, "-project-", "-version-", "-misuse-");

        self::assertEquals([['id' => 1, 'name' => 'test1']], $misuseTags);
    }

    function test_delete_misuse_tag()
    {
        $this->db->table('tags')->insert(['name' => 'test1']);
        $this->tagController->addTag('ex1', 1, '-project-', '-version-', '-misuse-', 'test1');

        $this->tagController->deleteMisuseTag([
            "tag" => 1,
            "exp" => 'ex1',
            "detector" => 1,
            "project" => "-project-",
            "version" => "-version-",
            "misuse" => "-misuse-"
        ]);

        $misuseTags = $this->db->getTagsForMisuse('ex1', 1, "-project-", "-version-", "-misuse-");
        self::assertEquals([], $misuseTags);
    }

    function test_adding_same_tag_twice()
    {
        $this->db->table('tags')->insert(['name' => 'test1']);
        $this->tagController->addTag('ex1', 1, '-project-', '-version-', '-misuse-', 'test1');

        $this->tagController->addTag('ex1', 1, '-project-', '-version-', '-misuse-', 'test1');

        $misuseTags = $this->db->getTagsForMisuse('ex1', 1, "-project-", "-version-", "-misuse-");
        self::assertEquals(1, count($misuseTags));
    }

    function test_add_unknown_tag()
    {
        $this->tagController->addTag('ex1', 1, '-project-', '-version-', '-misuse-', 'unknown_tag');

        $misuse_tags = $this->db->getTagsForMisuse('ex1', 1, "-project-", "-version-", "-misuse-");
        self::assertEquals([['id' => 1, 'name' => 'unknown_tag']], $misuse_tags);
    }
}
