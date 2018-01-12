<?php
/**
 * Created by PhpStorm.
 * User: jonasschlitzer
 * Date: 09.11.17
 * Time: 11:38
 */

namespace MuBench\ReviewSite\Old;


use MuBench\ReviewSite\Old\Detector;
use MuBench\ReviewSite\Old\DetectorDependent;

class Finding extends DetectorDependent
{
    protected $connection = 'old_db';

    protected function getTableName(Detector $detector)
    {
        return "detector_" . $detector->id;
    }

}