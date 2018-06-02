<?php

use Facebook\WebDriver\WebDriverBy;

require_once 'WebDriverTestCase.php';

class IndexTemplateTest extends WebDriverTestCase
{
    public function testAssertTitle()
    {
        $this->driver->get('http://localhost:8080');
        self::assertEquals("MUBench Review Site", $this->driver->getTitle());
    }

    public function testLoginUser()
    {
        $this->driver->get('http://admin:pass@localhost:8080/private/');
        $span = $this->driver->findElement(
            WebDriverBy::tagName('span')::className("right ")
        );
        $headlines = array("Reviewer: admin");
        self::assertEquals("Reviewer: admin", $span->getText());
    }
}