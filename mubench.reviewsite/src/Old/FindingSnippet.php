<?php
/**
 * Created by PhpStorm.
 * User: jonasschlitzer
 * Date: 09.11.17
 * Time: 17:06
 */

namespace MuBench\ReviewSite\Old;


use Illuminate\Database\Eloquent\Model;

class FindingSnippet extends Model
{

    protected $table = 'finding_snippets';
    protected $connection = 'old_db';

}