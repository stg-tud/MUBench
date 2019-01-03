<?php

namespace MuBench\ReviewSite\ViewExtensions;


class AnonymousViewExtension
{
    private $blind_mode;
    private $detector_blind_names;

    public function __construct($container)
    {
        $this->blind_mode = $container->settings['blind_mode']['enabled'];
        $this->detector_blind_names = $container->settings['blind_mode']['detector_blind_names'];
    }

    public function getDetectorName($detectorName)
    {
        if($this->blind_mode && array_key_exists($detectorName, $this->detector_blind_names)){
            return $this->detector_blind_names[$detectorName];
        }
        return $detectorName;
    }

    public function getReviewerName($reviewer)
    {
        if($this->blind_mode){
            return "reviewer-" . $reviewer->id;
        }
        return $reviewer->name;
    }

    public function getDetectorPathId($detector)
    {
        if($this->blind_mode){
            return $detector->id;
        }
        return $detector->muid;
    }

    public function getReviewerPathId($reviewer)
    {
        if($this->blind_mode){
            return $reviewer->id;
        }
        return $reviewer->name;
    }

}