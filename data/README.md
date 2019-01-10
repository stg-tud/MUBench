<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# Dataset Parametric Cryptographic API misuses

This Dataset in the MUBench data format references projects with known parametric cryptographic API misuses.
Each subfolder of this directory identifies one project.
For each project, the dataset references one version that contain the known misuse.
The dataset also specifies the misuses themselves and links misuses and project versions.

For more details on MUBench and the original dataset, visit [MUBench dataset](https://github.com/stg-tud/MUBench/tree/master/data).

## Filtering

When [running experiments](../mubench.pipeline/#run-experiments), we recommend to specify a subset of the entire MUBench dataset to run detectors on.

### Datasets

The easiest way is to use predefined experiment datasets, by passing their Id as an argument to the `--datasets` command-line option.
Available datasets are declared in the [datasets.yml](datasets.yml) file.
You may also add your own datasets to this file, by listing the [individual dataset entities](#individual-entities) you want to include.

Example: `$> ./mubench run ex2 DemoDetector --datasets TSE17-ExPrecision`

### Individual Entities

You may run experiments on individual dataset entities, by passing the entity Id as an argument to the `--only` command-line option.
Entities are projects, project versions, or misuses.
Their Ids are constructed as follows:

* The project Id is the name of the respective subfolder in this directory.
* The version Id has the form `<project-id>.<version-id>`, where the version Id is the name of the respective directory in `<project-id>/versions/`.
* The misuse Id has the form `<project-id>.<version-id>.<misuse-id>`, where the misuse Id is the name of the respective directory in `<project-id>/misuses/`.

Example: `$> ./mubench run ex1 DemoDetector --only aclang.587`

*Hint:* You may exclude individual entities using the `--skip` command-line option. Exclusion takes precedence over inclusion.


## Statistics

The MUBench dataset is continuously growing.
To get up-to-date statistics on the dataset, please [install the MUBench Pipeline](../mubench.pipeline/#setup) and run

    $> ./mubench stats general

Check `./mubench stats -h` for further details on other available dataset statistics and [filter options](#filtering).

## Parametric Cryptographic Misuse Details

<div itemscope itemtype="http://schema.org/Dataset">
  <h3 itemprop="name"> Parametric Cryptographic Misuses </h3>
  <p itemprop="description"> The parametric cryptographic misuse dataset contains misuses of cryptographic APIs due to passing a parameter to a function which is considered as insecure. All misuses are collected in 2018 in GitHub projects. </p>
  <a href="https://github.com/akwick/MUBench/tree/thesis-2018-dodhy/data" itemprop="url"> URL to the dataset folder </a>
  <p itemprop="version"> 1.0 </a>
  <p itemprop="creator"> Anam Dodhy and Anna-Katharina Wickert </p>
</div>
