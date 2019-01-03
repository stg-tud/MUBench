<?php

namespace MuBench\ReviewSite\Models;


class Finding extends DetectorDependent
{

    protected  function getTableName(Detector $detector)
    {
        return 'detector_' . $detector->id;
    }

    public function misuse()
    {
        $this->belongsTo(Misuse::class);
    }
}
