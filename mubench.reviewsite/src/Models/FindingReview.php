<?php
/**
 * Created by PhpStorm.
 * User: jonasschlitzer
 * Date: 30.09.17
 * Time: 13:48
 */

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class FindingReview extends Model
{
    public $timestamps = false;
    public $fillable = ['review_id', 'rank'];

    public function violation_types()
    {
        return $this->belongsToMany(Type::class, 'finding_review_types', 'finding_review_id', 'type_id');
    }
}
