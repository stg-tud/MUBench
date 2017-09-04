<?php

namespace MuBench\ReviewSite\Models;

class DetectorResult extends RunsResult
{
    /**
     * @var Detector
     */
    private $detector;

    public $runs;

    function __construct(Detector $detector, $runs)
    {
        parent::__construct($runs);
        $this->detector = $detector;
        $this->runs = $runs;
    }

    public function getDisplayName()
    {
        return $this->detector->muid;
    }
}
