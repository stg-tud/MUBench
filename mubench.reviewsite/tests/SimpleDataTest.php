<?php

require_once 'SlimTestCase.php';

class SimpleDataTest extends SlimTestCase
{

    function test_simple_test_data_script()
    {
        $app = $this->app;
        require __DIR__ . '/../bootstrap/bootstrap.php';
        require __DIR__ . '/../setup/create_database_tables.php';
        require 'create_simple_test_data.php';
    }

}
