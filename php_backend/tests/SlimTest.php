<?php
require_once "SlimTestCase.php";

class SlimTest extends SlimTestCase
{
    public function testIndex(){
        $this->get('/');
        $this->assertEquals('200', $this->response->getStatusCode());
    }

    public function testImpressum(){
        $this->get('/impressum/');
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

    public function testEx1WithAnyDataset(){
        $this->get('/ex1/any');
        $this->assertEquals('404', $this->response->getStatusCode());
    }

    public function testEx1WithAnyDatasetAndMuDetect(){
        $this->get('/ex1/any/MuDetect');
        $this->assertEquals('404', $this->response->getStatusCode());
    }

    public function testReview(){
        $this->get('/ex1/any/MuDetect/aclang/5/1');
        $this->assertEquals('404', $this->response->getStatusCode());
    }

    public function testReviewer(){
        $this->get('/ex1/any/MuDetect/aclang/5/1/admin');
        $this->assertEquals('404', $this->response->getStatusCode());
    }

}