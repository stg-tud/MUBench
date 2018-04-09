<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Metadata extends Model
{

    protected $fillable = ['misuse_muid', 'project_muid', 'version_muid', 'description', 'fix_description', 'file', 'method', 'diff_url'];

    public function correct_usages()
    {
        return $this->hasMany(CorrectUsage::class);
    }

    public function violation_types()
    {
        return $this->belongsToMany(Type::class, 'metadata_types', 'metadata_id', 'type_id');
    }

}
