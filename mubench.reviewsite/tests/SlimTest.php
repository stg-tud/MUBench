<?php

require_once "SlimTestCase.php";

class SlimTest extends SlimTestCase
{
    public function testIndex(){
        $this->get('/');
        $this->assertEquals('200', $this->response->getStatusCode());
    }
    
    public function testEx1(){
        $this->get('/ex1');
        $this->assertEquals('200', $this->response->getStatusCode());
    }

    public function testEx2(){
        $this->get('/ex2');
        $this->assertEquals('200', $this->response->getStatusCode());
    }

    public function testEx3(){
        $this->get('/ex3');
        $this->assertEquals('200', $this->response->getStatusCode());
    }

    public function testEx4NotFound(){
        $this->get('/ex4');
        $this->assertEquals('404', $this->response->getStatusCode());
    }

}