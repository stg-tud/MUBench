<?php

use Illuminate\Support\Facades\Schema;

class TableCreationHelper
{

    /** @var \Illuminate\Database\Schema\Builder */
    protected $schema;

    function __construct($connection)
    {
        $this->schema = Schema::connection($connection);
    }

    function dropIfExistsAndCreateNewWith($modelClass, $createFunc)
    {
        /** @var Illuminate\Database\Eloquent\Model $modelObj */
        $modelObj = new $modelClass;
        $this->dropIfExistsAndCreateTable($modelObj->getTable(), $createFunc);
    }

    function dropIfExistsAndCreateTable($tableName, $createFunc)
    {
        $this->schema->dropIfExists($tableName);
        $this->schema->create($tableName, $createFunc);
    }

}