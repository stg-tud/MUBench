<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class CorrectUsage extends Model
{
    public $table = "patterns";
    public $timestamps = false;

    public $fillable = ['metadata_id', 'code', 'line'];
}
