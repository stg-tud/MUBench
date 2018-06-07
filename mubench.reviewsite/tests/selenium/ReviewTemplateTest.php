<?php

use Facebook\WebDriver\WebDriverBy;

require_once 'WebDriverTestCase.php';

class ReviewTemplateTest extends WebDriverTestCase
{

    public function setUp()
    {
        parent::setUp();
        $this->getRoute("/experiments/1/detectors/TestDetector/projects/mubench/versions/42/misuses/1");
    }

    public function testAssertMisuse()
    {
        $misuseInfo = $this->driver->findElements(
            WebDriverBy::cssSelector("table.invisible > tbody > tr > td")
        );
        $misuse = ["Detector:", "TestDetector", "Target:", "project 'mubench' version 42", "Misuse:", "misuse '1'"];
        for($i = 0; $i < 6; $i++){
            self::assertEquals($misuse[$i], $misuseInfo[$i]->getText());
        }
    }

    public function testAssertPotentialHitsTable()
    {
        $row = $this->driver->findElements(
            WebDriverBy::cssSelector("table.potential_hits > tbody > tr > td")
        );
        $hitValues = ["?", "1", "test_column"];
        self::assertEquals(3, count($row));
        for($i = 0; $i < 3; $i++){
            self::assertEquals($hitValues[$i], $row[$i]->getText());
        }
    }

    public function testShowCommentModal()
    {
        $this->getRoute("/experiments/1/detectors/TestDetector/projects/mubench/versions/42/misuses/1", true);
        $commentDiv = $this->driver->findElement(
            WebDriverBy::cssSelector("div#comment-area")
        );
        self::assertFalse($commentDiv->isDisplayed());
        $commentButton = $this->driver->findElement(
            WebDriverBy::cssSelector('a[onclick="comment()"]')
        );
        $commentButton->click();
        self::assertTrue($commentDiv->isDisplayed());
    }

    public function testShowCommentModalWarning()
    {
        $this->getRoute("/experiments/1/detectors/TestDetector/projects/mubench/versions/42/misuses/1", true);
        $commentWarning = $this->driver->findElement(
            WebDriverBy::cssSelector("div#comment-area div#overlay-button")
        );
        self::assertNotNull($commentWarning);
    }

}
