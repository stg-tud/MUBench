<?php

namespace MuBench\ReviewSite\Model;

class ExperimentResult extends RunsResult
{
    private $number_of_detectors;

    function __construct(array $detector_results)
    {
        $runs = array();
        foreach ($detector_results as $detector_result) {
            $runs = array_merge($runs, $detector_result->runs);
        }
        parent::__construct($runs);
        $this->number_of_detectors = count($detector_results);
    }

    public function getDisplayName()
    {
        return "Total";
    }

    public function getRecall()
    {
        return parent::getRecall() / $this->number_of_detectors;
    }
}
