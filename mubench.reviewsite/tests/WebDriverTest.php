<?php

use Facebook\WebDriver\Remote\DesiredCapabilities;
use Facebook\WebDriver\Remote\RemoteWebDriver;
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
}