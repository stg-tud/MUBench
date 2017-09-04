<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Pattern extends Model
{
    public $timestamps = false;

    public $fillable = ['metadata_id', 'code', 'line'];
}
