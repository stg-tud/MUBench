<?php

namespace MuBench\ReviewSite\Model;

class DetectorResult extends RunsResult
{
    /**
     * @var Detector
     */
    private $detector;

    /**
     * @var array
     */
    public $runs;

    function __construct(Detector $detector, array $runs)
    {
        parent::__construct($runs);
        $this->detector = $detector;
        $this->runs = $runs;
    }

    public function getDisplayName()
    {
        return $this->detector->name;
    }
}
