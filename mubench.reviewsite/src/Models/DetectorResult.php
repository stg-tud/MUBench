<?php

namespace MuBench\ReviewSite\Models;

class DetectorResult extends RunsResult
{
    /**
     * @var Detector
     */
    private $detector;

    public $runs;

    function __construct(Detector $detector, $runs, $required_reviews)
    {
        parent::__construct($runs, $required_reviews);
        $this->detector = $detector;
        $this->runs = $runs;
    }

    public function getDisplayName()
    {
        return $this->detector->muid;
    }
}
