<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Snippet extends Model
{
    public $timestamps = false;
    public $fillable = ['project_muid', 'version_muid', 'misuse_muid', 'snippet', 'line', 'file'];
}
