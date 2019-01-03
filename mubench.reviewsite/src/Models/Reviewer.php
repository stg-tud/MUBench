<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Reviewer extends Model
{
    const RESOLUTION_REVIEWER_NAME = 'resolution';

    public $timestamps = false;
    protected $fillable = ['name'];

    public function reviews()
    {
        return $this->hasMany(Review::class);
    }

    public function isResolutionReviewer()
    {
        return $this->name === self::RESOLUTION_REVIEWER_NAME;
    }

    public static function getResolutionReviewer()
    {
        return Reviewer::firstOrCreate(['name' => self::RESOLUTION_REVIEWER_NAME]);
    }

    public static function findByIdOrName($reviewer_id)
    {
        $reviewer = Reviewer::find($reviewer_id);
        if(!$reviewer){
            return Reviewer::where('name', $reviewer_id)->first();
        }
        return $reviewer;
    }
}
