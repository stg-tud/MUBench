<?php
/**
 * Created by PhpStorm.
 * User: jonasschlitzer
 * Date: 09.11.17
 * Time: 17:45
 */

namespace MuBench\ReviewSite\Old;


use Illuminate\Database\Eloquent\Model;

class FindingReviewType extends Model
{

    protected $table = 'review_findings_types';
    protected $connection = 'old_db';

}