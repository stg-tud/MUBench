<?php

namespace MuBench\ReviewSite\Models;


class Run extends DetectorDependent
{
    protected  function getTableName(Detector $detector)
    {
        return 'stats_' . $detector->id;
    }

    public function misuses()
    {
        return $this->hasMany(Misuse::class, 'run_id', 'id')->where('detector_muid', $this->detector->muid);
    }
}
