<?php
/**
 * Created by PhpStorm.
 * User: jonasschlitzer
 * Date: 09.11.17
 * Time: 17:15
 */

namespace MuBench\ReviewSite\Old;


use Illuminate\Database\Eloquent\Model;

class MetadataSnippet extends Model
{

    protected $table = 'meta_snippets';
    protected $connection = 'old_db';

}