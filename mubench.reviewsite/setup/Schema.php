<?php

namespace MuBench\ReviewSite\Setup;

use Illuminate\Support\Facades\Schema as DBSchema;

class Schema
{

    /** @var \Illuminate\Database\Schema\Builder */
    protected $dbSchema;

    function __construct($connection)
    {
        $this->dbSchema = DBSchema::connection($connection);
    }

    public function dropIfExistsAndCreateTable($table, $createFunc)
    {
        if(class_exists($table)){
            /** @var Illuminate\Database\Eloquent\Model $modelObj */
            $modelObj = new $table;
            $table = $modelObj->getTable();
        }
        $this->dbSchema->dropIfExists($table);
        $this->dbSchema->create($table, $createFunc);
    }

}