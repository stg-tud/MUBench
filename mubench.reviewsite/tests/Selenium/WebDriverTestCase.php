<?php

namespace MuBench\ReviewSite\Tests\Selenium;

use Facebook\WebDriver\Remote\DesiredCapabilities;
use Facebook\WebDriver\Remote\RemoteWebDriver;
use PHPUnit\Framework\TestCase;

class WebDriverTestCase extends TestCase
{
    /**
     * @var RemoteWebDriver
     */
    protected $driver;

    protected $host = "localhost:8080";

    public function __construct()
    {
        parent::__construct();
        $chromeOptions = new \Facebook\WebDriver\Chrome\ChromeOptions();
        $chromeOptions->addArguments(array('headless' , '-no-sandbox')); //
        $capabilities = DesiredCapabilities::chrome();
        $capabilities->setCapability(\Facebook\WebDriver\Chrome\ChromeOptions::CAPABILITY, $chromeOptions);
        $this->driver = RemoteWebDriver::create("http://localhost:4444/wd/hub",
            $capabilities, 5000
        );
        $this->getRoute("/setup/setup.php");
        $this->getRoute("/tests/create_test_data.php");
    }

    public function __destruct()
    {
        $this->driver->quit();
    }

    protected function buildUrl($route, $private = false, $user = "admin", $pass = "pass")
    {
        if($private){
            return "http://{$user}:{$pass}@{$this->host}/private{$route}";
        }
        return "http://{$this->host}{$route}";
    }

    protected function getRoute($route, $private = false, $user = "admin", $pass = "pass")
    {
        $this->driver->get($this->buildUrl($route, $private, $user, $pass));
    }

    protected function assertRoute($route, $private = false, $user = "admin", $pass = "pass")
    {
        self::assertEquals($this->buildUrl($route, $private, $user, $pass), $this->driver->getCurrentURL());
    }

}
