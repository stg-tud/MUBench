<?php

namespace MuBench\ReviewSite\Model;


class Detector
{
    public $name;
    public $id;

    public function __construct($name, $id)
    {
        $this->id = $id;
        $this->name = $name;
    }
}
