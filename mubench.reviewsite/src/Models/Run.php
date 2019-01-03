<?php

namespace MuBench\ReviewSite\Models;


class Run extends DetectorDependent
{
    protected  function getTableName(Detector $detector)
    {
        return 'runs_' . $detector->id;
    }

    public function misuses()
    {
        return $this->hasMany(Misuse::class, 'run_id', 'id')->where('detector_id', $this->detector->id);
    }
}
