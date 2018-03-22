<?php

namespace MuBench\ReviewSite\Controllers;

class Controller
{
    private $container;

    public function __construct($container)
    {

        $this->container = $container;
    }

    public function __get($property)
    {
        if ($this->container->{$property}) {
            return $this->container->{$property};
        }
        return null;
    }

    function detectorBlindToReal($detector_name)
    {
        if($this->settings['blind_mode']['enabled']){
            foreach($this->settings['blind_mode']['detector_blind_names'] as $detector => $blind_name){
                if($blind_name === $detector_name){
                    return $detector;
                }
            }
        }
        return $detector_name;
    }
}
