<?php

namespace MuBench\ReviewSite\Old;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use MuBench\ReviewSite\Models\Experiment;

// SMELL this is both dependent on a detector and an experiment. Find a better name?
abstract class DetectorDependent extends Model
{
    protected $detector;
    protected $connection = 'old_db';

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

}
