<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class Detector extends Model
{
    public $timestamps = false;
    public $incrementing = false;
    protected $fillable = ['muid'];
    protected $primaryKey = 'muid';

    public static function boot()
    {
        parent::boot();
        static::creating(function($detector){
            $lastId = DB::table($detector->getTable())->max('id');
            $detector->id = $lastId + 1;
        });
    }

    public static function withRuns(Experiment $experiment)
    {
        return Detector::all()->filter(function(Detector $detector) use ($experiment) {
            return $detector->hasRuns($experiment);
        })->sortBy('muid');
    }

    public function hasRuns(Experiment $experiment)
    {
        return Run::of($this)->in($experiment)->exists();
    }

    public static function withFindings(Experiment $experiment)
    {
        return Detector::all()->filter(function(Detector $detector) use ($experiment) {
            return $detector->hasResults($experiment);
        })->sortBy('muid');
    }

    public function hasResults(Experiment $experiment)
    {
        return Finding::of($this)->in($experiment)->exists();
    }
}
