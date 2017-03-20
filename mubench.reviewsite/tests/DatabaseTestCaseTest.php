<?php

require_once 'DatabaseTestCase.php';

class DatabaseTestCaseTest extends DatabaseTestCase
{

    function testTablesExist()
    {
        $tables = $this->table('sqlite_master')->select('name')->where('type', '=', 'table')->get();
        $actual = [];
        foreach($tables as $t){
            $actual[] = $t;
        }

        $expectedTables = [
            ['name' => 'detectors'],
            ['name' => 'stats'],
            ['name' => 'metadata'],
            ['name' => 'patterns'],
            ['name' => 'reviews'],
            ['name' => 'review_findings'],
            ['name' => 'review_findings_types'],
            ['name' => 'meta_snippets'],
            ['name' => 'finding_snippets'],
            ['name' => 'types']
        ];

        self::assertEquals($expectedTables, $actual);
    }

    function testTypesInserted()
    {
        $types = $this->table('types')->select('name')->get();
        $actual = [];
        foreach($types as $t){
            $actual[] = $t;
        }

        $expectedTypes = [
            ['name' => 'missing/call'],
            ['name' => 'misplaced/call'],
            ['name' => 'superfluous/call'],
            ['name' => 'missing/condition/null_check'],
            ['name' => 'missing/condition/value_or_state'],
            ['name' => 'missing/condition/synchronization'],
            ['name' => 'missing/condition/context'],
            ['name' => 'misplaced/condition/null_check'],
            ['name' => 'misplaced/condition/value_or_state'],
            ['name' => 'misplaced/condition/synchronization'],
            ['name' => 'misplaced/condition/context'],
            ['name' => 'superfluous/condition/null_check'],
            ['name' => 'superfluous/condition/value_or_state'],
            ['name' => 'superfluous/condition/synchronization'],
            ['name' => 'superfluous/condition/context'],
            ['name' => 'missing/exception_handling'],
            ['name' => 'misplaced/exception_handling'],
            ['name' => 'superfluous/exception_handling'],
            ['name' => 'missing/iteration'],
            ['name' => 'misplaced/iteration'],
            ['name' => 'superfluous/iteration']
        ];

        self::assertEquals($expectedTypes, $actual);
    }

    private function table($table)
    {
        return $this->pdo->table($table)->setFetchMode(PDO::FETCH_ASSOC);
    }
}