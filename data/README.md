<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Dataset

The MUBench Dataset references projects with known API misuses.
Each subfolder of this directory identifies one project.
For each project, the dataset references one or more project versions that contain the known misuses (usually the version immediately before a particular misuse was fixed).
The dataset also specifies the misuses themselves and links misuses and project versions.

Building up the MUBench dataset required imense manual effort.
Any [contribution](#contribute) is welcome.
At this point, we want to thank several people for their support:

* Mattis Kämmerer and Jonas Schlitzer for their hard work to try compile tons of arbitrary project checkouts.
* Michael Pradel for providing list of findings from his previous studies.
* Owolabi Legunsen for providing the dataset from ["How Good are the Specs? A Study of the Bug-Finding Effectiveness of Existing Java API Specifications" (ASE'16)](http://fsl.cs.illinois.edu/spec-eval/)


## Filtering

When [running experiments](../mubench.pipeline/#run-experiments), we recommend to specify a subset of the entire MUBench dataset to run detectors on.

### Datasets

The easiest way is to use predefined experiment datasets, by passing their Ids to the `--datasets` command-line option.
Available datasets are declared in the [datasets.yml](datasets.yml) file.

Example: `mubench> pipeline run ex2 DemoDetector --datasets TSE17-ExPrecision`

### Individual Entities

You may run experiments on individual dataset entities, by passing the entity Id as an argument to the `--only` command-line option.
Entities are projects, project versions, or misuses.
Their Ids are constructed as follows:

* The project Id is the name of the respective subfolder in this directory.
* The version Id has the form `<project-id>.<version-id>`, where the version Id is the name of the respective directory in `<project-id>/versions/`.
* The misuse Id has the form `<project-id>.<version-id>.<misuse-id>`, where the misuse Id is the name of the respective directory in `<project-id>/misuses/`.

Example: `mubench> pipeline run ex1 DemoDetector --only aclang.587`

*Hint:* You may exclude individual entities using the `--skip` command-line option. Exclusion takes precedence over inclusion.


## Statistics

The MUBench dataset is continuously growing.
To get up-to-date statistics on the dataset, please [install the MUBench Pipeline](../mubench.pipeline/#setup) and run

    mubench> pipeline stats general

Check `pipeline stats -h` for further details on other available dataset statistics and [filter options](#filtering).

We subsequently report statistics on the subsets of the MUBench Dataset that were used in previous publications.

### MUBench: A Benchmark for API-Misuse Detectors

Details: ['*MUBench: A Benchmark for API-Misuse Detectors*'](http://sven-amann.de/publications/2016-05-MSR-MUBench-dataset.html) ([MSR '16 Data Showcase](http://2016.msrconf.org/#/data))

* *Initial dataset*: 90 misuses (73 from 55 versions of 21 projects, 17 hand-crafted examples)

### A Systematic Evaluation of Static API-Misuse Detectors

Details: ["A Systematic Evaluation of Static API-Misuse Detectors"](http://sven-amann.de/publications/2018-03-A-Systematic-Evalution-of-Static-API-Misuse-Detectors/), TSE, 2018

Dataset considered in the creation of the API Misuse Classification (MUC):

* *Extended dataset*: 100 misuses (73 from 55 versions of 21 projects, 27 hand-crafted examples)

Datasets used to benchmark the detectors DMMC, GrouMiner, Jadet, and Tikanga (includes only compilable project versions):

* *Experiment P (precision)*
  * Dataset `TSE17-ExPrecision`, contains 5 projects
  * Dataset `TSE17-ExPrecision-TruePositives` contains 14 previously-unknown misuses identified in the detectors' top-20 findings on the above 5 projects
* *Experiment RUB (recall upper bound)*
  * Dataset `TSE17-ExRecallUpperBound` contains 64 misuses (39 from 29 versions of 13 projects, 25 hand-crafted examples)
* *Experiment R (recall)*
  * Dataset `TSE17-ExRecall` contains 53 misuses (all from 29 versions of 13 projects, no hand-crafted examples)'


## Contribute

To contribute to the MUBench Dataset, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) with details about the misuses.
For each misuse, please try to provide

* A description of the misuse (and its fix).
* A link to the website of the project you found the misuse in.
* A link to the project's publicly-readable version-control system, and a commit id to a version with the misuse or, ideally, to the commit that fixes the misuse.
* The misuse's location (file, method, and misused API).
* Instructions on how to compile the project in the respective version.

You may also add your own datasets to the [datasets.yml](datasets.yml) file, by listing the [individual dataset entities](#individual-entities) you want to include.
