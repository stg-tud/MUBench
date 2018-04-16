<img align="right" width="320" height="320" alt="MUBench Logo" src="./meta/logo.png?raw=true" />

# MUBench

An automated benchmark for API-misuse detectors.

Please feel free to [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann), if you have any questions.

CI Status: [![CI Status](https://api.shippable.com/projects/570d22d52a8192902e1bfa79/badge?branch=master)](https://app.shippable.com/projects/570d22d52a8192902e1bfa79)

## Contributors

* [Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) (Project Lead)
* [Sarah Nadi](http://www.sarahnadi.org/)
* [Hoan Anh Nguyen](https://sites.google.com/site/nguyenanhhoan/)
* [Tien N. Nguyen](http://home.eng.iastate.edu/~tien/)
* [Mattis Kämmerer](https://github.com/M8is)
* [Jonas Schlitzer](https://github.com/joschli)

## Publications

* ['*MUBench: A Benchmark of API-Misuse Detectors*'](http://sven-amann.de/publications/2016-05-MSR-MUBench-dataset.html) ([MSR '16 Data Showcase](http://2016.msrconf.org/#/data))
* ['*A Systematic Evaluation of Static API-Misuse Detectors*'](https://arxiv.org/abs/1712.00242) (TSE '18)

## Getting Started

With MUBench, you may run [different API-misuse detectors](detectors/) in [a number of experiments](mubench.pipeline/#experiments) to determine their precision and recall.
To this end, MUBench provides [a curated dataset of real-world projects and known misuses](data/).
In each experiment run, the respective detector emits findings which you need to review manually.
To this end, MUBench publishes (a subset of) the findings to [a review website](mubench.reviewsite/).
After you completed your reviews, the site automatically computes experiment statistics.

### Setup

1. [Setup a review (web)site](mubench.reviewsite/#setup) to publish detector findings to
2. [Setup the experiment pipeline](mubench.pipeline/#setup) to run experiments

### Use

1. [Run experiments](mubench.pipeline/#run-experiments), using `./mubench run`
2. [Publish detector findings to your review site](mubench.reviewsite/#publish-detector-findings), using `./mubench publish`

## Contribute

We want MUBench to grow, so please be welcome to

* [Add Your Own Project or Misuse to the Dataset](data/).
* [Add Your Own Detector to the Benchmark](mubench.cli/).

## License

All software provided in this repository is subject to the [CRAPL license](CRAPL-LICENSE.txt).

The detectors included in MuBench are subject to the licensing of their respective creators. See the information in [the detectors' folders](detectors).

The projects referenced in the MuBench dataset are subject to their respective licenses.

The project artwork is subject to the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
