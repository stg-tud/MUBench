<?php

require_once "SlimTestCase.php";

class SlimTest extends SlimTestCase
{
    public function testIndex()
    {
        $this->get('/');
        $this->assertEquals('200', $this->response->getStatusCode());
    }

    public function testNotFound()
    {
        $this->get('/test/t');
        $this->assertEquals('404', $this->response->getStatusCode());
    }
}