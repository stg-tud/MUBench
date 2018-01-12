<?php
/**
 * Created by PhpStorm.
 * User: jonasschlitzer
 * Date: 09.11.17
 * Time: 17:21
 */

namespace MuBench\ReviewSite\Old;


use Illuminate\Database\Eloquent\Model;

class Review extends Model
{

    protected $connection = 'old_db';

    public function finding_reviews()
    {
        return $this->hasMany(FindingReview::class, 'review', 'id');
    }
}