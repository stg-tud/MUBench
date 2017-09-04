<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Reviewer extends Model
{

    public $timestamps = false;
    protected $fillable = ['name'];

    public function reviews()
    {
        return $this->hasMany(Review::class);
    }

}
