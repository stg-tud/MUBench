<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Dataset

The MUBench Dataset references projects with known API misuses. Each subfolder of this directory identifies one project. For each project, the dataset references one or more project versions that contain the known misuses (usually the version immediately before a particular misuse was fixed). The dataset also specifies the misuses themselves and links misuses and project versions.

When running experiments you may use the qualified project, version, or misuse ids to select particular datapoints for your experiment. The project id is the name of the respective subfolder in this directory. The qualified version id has the form `<project-id>.<version-id>`, where the version id is the name of the respective directory in `<project-id>/versions/`. The qualified misuse id has the form `<project-id>.<misuse-id>`, where the misuse id is the name of the respective directory in `<project-id>/misuses/`.

You may also use qualified project, version, or misuse ids to specify sub-dataset in [datasets.yml](datasets.yml), to conveniently run experiments on certain subsets of the entire dataset.

## Contribute

To contribute to the MUBench Dataset, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) with details about the misuses. For each misuse, please try to provide

* A description of the misuse (and its fix).
* A link to the website of the project you found the misuse in.
* A link to the project's publicly-readable version-control system, and a commit id to a version with the misuse or, ideally, to the commit that fixes the misuse.
* The misuse's location (file, method, and misused API).
* Instructions on how to compile the project in the respective version.
