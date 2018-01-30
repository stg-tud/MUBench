<?php

require_once 'SlimTestCase.php';

class SimpleDataTest extends SlimTestCase
{

    public function setUp()
    {
        parent::setUp();
    }

    function test_simple_test_data_script()
    {
        $app = $this->app;
        require __DIR__ . '/../bootstrap/bootstrap.php';
        include __DIR__ . '/../setup/create_database_tables.php';
        include 'create_simple_test_data.php';
    }

}