<?php

namespace MuBench\ReviewSite\Model;


class Experiment
{

    private $id;
    private $number;
    private $title;

    public static function all()
    {
        return [
            "ex1" => new Experiment("ex1", 1, "Provided Patterns"),
            "ex2" => new Experiment("ex2", 2, "All Findings"),
            "ex3" => new Experiment("ex3", 3, "Benchmark")
        ];
    }

    public static function get($experiment_id)
    {
        return Experiment::all()[$experiment_id];
    }

    function __construct($id, $number, $title)
    {
        $this->id = $id;
        $this->number = $number;
        $this->title = $title;
    }

    public function getId()
    {
        return $this->id;
    }

    public function getNumber()
    {
        return $this->number;
    }

    public function getTitle()
    {
        return $this->title;
    }
}
