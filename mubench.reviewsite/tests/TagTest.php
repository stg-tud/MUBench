<?php

namespace MuBench\ReviewSite\Tests;

use MuBench\ReviewSite\Models\Tag;

class TagTest extends SlimTestCase
{


    public function testFontColorBlack()
    {
        $tag = new Tag();
        $tag->color = '#ffffff';
        self::assertEquals('black', $tag->getFontColor());
    }

    public function testFontColorShortHexBlack()
    {
        $tag = new Tag();
        $tag->color = '#fff';
        self::assertEquals('black', $tag->getFontColor());
    }

    public function testFontColorWhite()
    {
        $tag = new Tag();
        $tag->color = '#000000';
        self::assertEquals('white', $tag->getFontColor());
    }


    public function testFontColorShortHexWhite()
    {
        $tag = new Tag();
        $tag->color = '#000';
        self::assertEquals('white', $tag->getFontColor());
    }
}