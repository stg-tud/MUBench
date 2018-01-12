<?php
/**
 * Created by PhpStorm.
 * User: jonasschlitzer
 * Date: 09.11.17
 * Time: 17:39
 */

namespace MuBench\ReviewSite\Old;


use Illuminate\Database\Eloquent\Model;
use MuBench\ReviewSite\Models\Type;

class FindingReview extends Model
{

    protected $table = 'review_findings';
    protected $connection = 'old_db';

    public function review_types()
    {
        return $this->hasMany(FindingReviewType::class, 'review_finding', 'id');
    }

}