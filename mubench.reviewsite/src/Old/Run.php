<?php

namespace MuBench\ReviewSite\Old;


use Illuminate\Database\Eloquent\Model;
use MuBench\ReviewSite\Old\Detector;
use MuBench\ReviewSite\Old\DetectorDependent;

class Run extends DetectorDependent
{

    protected $connection = 'old_db';

    protected function getTableName(Detector $detector)
    {
        return 'stats_' . $detector->id;
    }
}