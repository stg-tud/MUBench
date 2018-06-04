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

    public function testLoginUser()
    {
        $this->getRoute("/", true);
        $span = $this->driver->findElement(
            WebDriverBy::tagName('span')::className("right ")
        );
        self::assertEquals("Reviewer: admin", $span->getText());
    }
}