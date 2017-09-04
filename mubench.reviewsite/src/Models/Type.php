<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Type extends Model
{
    public $fillable = ['name'];
    public $timestamps = false;

    public function metadata(){
        return $this->belongsToMany(Metadata::class, 'metadata_types', 'type_id', 'metadata_id');
    }
}
