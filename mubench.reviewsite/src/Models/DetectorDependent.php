<?php

namespace MuBench\ReviewSite\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

// SMELL this is both dependent on a detector and an experiment. Find a better name?
abstract class DetectorDependent extends Model
{
    protected $detector;

    public static function of(Detector $detector)
    {
        $instance = new static;
        $instance->setDetector($detector);
        return $instance->newQuery();
    }

    public function setDetector(Detector $detector)
    {
        $this->detector = $detector;
        if ($detector != null) {
            $this->table = $this->getTableName($detector);
        }
    }

    protected abstract function getTableName(Detector $detector);

    public function newInstance($attributes = [], $exists = false)
    {
        /** @var DetectorDependent $instance */
        $instance = parent::newInstance($attributes, $exists);
        $instance->setDetector($this->detector);
        return $instance;
    }

    public function scopeIn(Builder $query, Experiment $experiment)
    {
        return $query->where('experiment_id', $experiment->id);
    }

    public function experiment()
    {
        return $this->belongsTo(Experiment::class);
    }
}
