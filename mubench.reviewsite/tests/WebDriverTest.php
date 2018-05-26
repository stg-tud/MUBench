<?php

use Facebook\WebDriver\Remote\DesiredCapabilities;
use Facebook\WebDriver\Remote\RemoteWebDriver;
use Facebook\WebDriver\WebDriverBy;
use PHPUnit\Framework\TestCase;

class WebDriverTest extends TestCase
{
    /**
     * @var RemoteWebDriver
     */
    protected $driver;

    public function setUp()
    {
        $chromeOptions = new \Facebook\WebDriver\Chrome\ChromeOptions();
        $chromeOptions->addArguments(array('headless' , '-no-sandbox')); //
        $capabilities = DesiredCapabilities::chrome();
        $capabilities->setCapability(\Facebook\WebDriver\Chrome\ChromeOptions::CAPABILITY, $chromeOptions);
        $this->driver = RemoteWebDriver::create("http://localhost:4444/wd/hub",
            $capabilities, 5000
        );
    }

    public function tearDown()
    {
        $this->driver->quit();
    }

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