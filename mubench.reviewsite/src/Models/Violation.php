<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Violation extends Model
{
    protected $table = "types";
    public $fillable = ['name'];
    public $timestamps = false;

    public function metadata(){
        return $this->belongsToMany(Metadata::class, 'metadata_types', 'type_id', 'metadata_id');
    }
}
