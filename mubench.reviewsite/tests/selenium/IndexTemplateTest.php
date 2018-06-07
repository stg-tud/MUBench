<?php

use Facebook\WebDriver\WebDriverBy;

require_once 'WebDriverTestCase.php';

class IndexTemplateTest extends WebDriverTestCase
{
    public function testAssertTitle()
    {
        $this->getRoute("/");
        self::assertEquals("MUBench Review Site", $this->driver->getTitle());
    }

    public function testAssertMenu()
    {
        $this->getRoute("/");
        $menu_links = $this->driver->findElements(
            WebDriverBy::cssSelector('ul > li')
        );

        self::assertEquals(14, count($menu_links));
    }

    public function testLoginUser()
    {
        $this->getRoute("/", true);
        $span = $this->driver->findElement(
            WebDriverBy::tagName('span')::className("right ")
        );
        self::assertEquals("Reviewer: admin", $span->getText());
    }

    public function testLoggedInShowReviewState()
    {
        $this->getRoute("/", true);
        $needs_review_icons = $this->driver->findElements(
            WebDriverBy::tagName('i')::className("fa-search")
        );
        $disagreement_icons = $this->driver->findElements(
            WebDriverBy::tagName('i')::className("fa-exclamation-triangle")
        );
        self::assertEquals(4, count($needs_review_icons));
        self::assertEquals(2, count($disagreement_icons));
    }
}
