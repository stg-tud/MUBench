<?php

namespace MuBench\ReviewSite\Controller;

use DatabaseTestCase;
use MuBench\ReviewSite\Model\Detector;

class TagTest extends DatabaseTestCase
{
    /** @var MisuseTagsController */
    private $tagController;

    /** @var Detector */
    private $detector;

    function setUp()
    {
        parent::setUp();
        $this->tagController = new MisuseTagsController($this->db, $this->logger, "-site-base-url-");
        $this->detector = $this->db->getOrCreateDetector('-d-');
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
        $this->tagController->addTag('ex1', $this->detector, '-project-', '-version-', '-misuse-', 'test1');

        $misuseTags = $this->tagController->getTags('ex1', $this->detector, "-project-", "-version-", "-misuse-");
        self::assertEquals([['id' => 1, 'name' => 'test1']], $misuseTags);
    }

    function test_delete_misuse_tag()
    {
        $this->db->table('tags')->insert(['name' => 'test1']);
        $this->tagController->addTag('ex1', $this->detector, '-project-', '-version-', '-misuse-', 'test1');

        $this->tagController->deleteTag('ex1', $this->detector, '-project-', '-version-', '-misuse-', 'test1');

        $misuseTags = $this->tagController->getTags('ex1', $this->detector, "-project-", "-version-", "-misuse-");
        self::assertEquals([], $misuseTags);
    }

    function test_adding_same_tag_twice()
    {
        $this->db->table('tags')->insert(['name' => 'test1']);
        $this->tagController->addTag('ex1', $this->detector, '-project-', '-version-', '-misuse-', 'test1');

        $this->tagController->addTag('ex1', $this->detector, '-project-', '-version-', '-misuse-', 'test1');

        $misuseTags = $this->tagController->getTags('ex1', $this->detector, "-project-", "-version-", "-misuse-");
        self::assertEquals(1, count($misuseTags));
    }

    function test_add_unknown_tag()
    {
        $this->tagController->addTag('ex1', $this->detector, '-project-', '-version-', '-misuse-', 'unknown_tag');

        $misuse_tags = $this->tagController->getTags('ex1', $this->detector, "-project-", "-version-", "-misuse-");
        self::assertEquals([['id' => 1, 'name' => 'unknown_tag']], $misuse_tags);
    }
}
