<?php

use Illuminate\Support\Facades\Schema;

require_once 'SlimTestCase.php';

class SimpleDataTest extends SlimTestCase
{

    function test_simple_test_data_script()
    {
        $schema = Schema::connection('default');
        require __DIR__ . '/../setup/create_database_tables.php';
        $app = $this->app;
        $container = $this->app->getContainer();
        $capsule = Schema::getFacadeApplication()['db'];
        require 'create_simple_test_data.php';
    }

}