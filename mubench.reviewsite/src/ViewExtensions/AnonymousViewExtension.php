<?php

namespace MuBench\ReviewSite\ViewExtensions;


class AnonymousViewExtension extends ViewExtension
{
    private function isInBlindMode()
    {
        return $this->settings['blind_mode']['enabled'];
    }

    public function getDetectorName($detectorName)
    {
        $detector_blind_names = $this->settings['blind_mode']['detector_blind_names'];
        if($this->isInBlindMode() && array_key_exists($detectorName, $detector_blind_names)){
            return $detector_blind_names[$detectorName];
        }
        return $detectorName;
    }

    public function getReviewerName($reviewer)
    {
        if($this->isInBlindMode()){
            return "reviewer-" . $reviewer->id;
        }
        return $reviewer->name;
    }

    public function getDetectorPathId($detector)
    {
        if($this->isInBlindMode()){
            return $detector->id;
        }
        return $detector->muid;
    }

    public function getReviewerPathId($reviewer)
    {
        if($this->isInBlindMode()){
            return $reviewer->id;
        }
        return $reviewer->name;
    }
}
