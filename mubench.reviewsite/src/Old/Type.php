<?php

namespace MuBench\ReviewSite\Old;


use Illuminate\Database\Eloquent\Model;

class Type extends Model
{
    protected $connection = 'old_db';
    public $fillable = ['name'];
    public $timestamps = false;
}
