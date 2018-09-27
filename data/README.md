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

We want the MUBench Dataset to grow and to stay current, thus, we welcome any contribution to the dataset.
If you found a previously unknown misuse or a mistake in the existing dataset, we encourage you to [integrate the change and create a Pull Request](#data-pull-request).
If you lack the time for this, we encourage you to [submit an issue with the respective information](#data-issue).
Note, however, that we can integrate Pull Requests much faster.


### Data Pull Request

The change the MUBench dataset, we recommend the following procedure:

1. [Fork the project](https://github.com/stg-tud/MUBench/fork).
2. [Add projects](#add-a-project), [project versions](#add-a-version), [misuses](#add-a-misuse), and [datasets](#add-a-dataset).
3. [Validate your change (and use it for running experiments)](#data-validation).
4. Create a pull request.

*Hint:* Most data in the MUBench dataset is stored in [the YAML format](http://yaml.org/).

*Hint:* We recommend that you set up the validation step early on and use it while adding to the dataset, to identify and fix mistakes as early as possible.

#### Add a Project

To add a new project to the dataset:

1. Create a subdirectory in `data/` and name it after the project, say, `data/myproject`.
   The directory name is used as the project's Id in the MUBench Dataset, therefore, we recommend choosing a name that is easy to remember and type.
   The name must not contain whitespaces or dots.
2. Create the file `data/myproject/project.yml` and add the project name, website, and version-control system information.

       name: My Project
       repository:
         type: git
         url: https://github.com/my-org/my-project.git
       url: https://my.org/my-project

   [The MUBench Pipeline](../mubench.pipeline) supports `git`, `svn`, and `zip` (for source bundles), as the repository type.
3. [Add at least one version to the project](#add-a-version), for it to become usable in the benchmark.

*Hint:* See any of the `project.yml` files of the existing projects for reference.

#### Add a Version

MUBench understands a project version as a snapshot of the respective project as identified by a commit Id in the version control system.
To add a new project version for the project `myproject` to the dataset:

1. Create a subdirectory in `data/myproject/versions` and name it after the version, say, `data/myproject/versions/v42_5`.
   The directory name is used as the version's Id in the MUBench Dataset, therefore, we recommend choosing a name that is easy to remember and type.
   Many project versions in the dataset are named after the commit Id or an issue-report Id.
   The name must not contain whitespaces or dots.
2. Create the file `data/myproject/versions/v42_5/version.yml` and add the revision (commit Id) and build instructions.

       revision: 045d2ec6e1b1dc9294a2cabbe3112a1e2ee509f7
       build:
         src: src/main/java/
         commands:
         - mvn compile
         classes: $mvn.default.classes

   The revision is used to retrieve the respective project version's source code from the version-control system specified in the `project.yml` file, e.g., via `git clone/checkout` or `svn checkout`.
   If the repository type is `zip`, the revision is the URL to a source archive to download and uncompress.
   The build instructions consist of three parts:
   * A single path or a list of paths to the source directories, i.e., paths to package roots.
   * A list of instructions to compile the project (or the project modules relevant to the benchmark).
     See our detailled [discussion of the compilation process](#compile-a-version) below.
   * A single path or a list of paths to the classes directories, i.e., the compile output directories.
     Since these paths sometimes depend on the version of the build tool, you may use the placeholders `$mvn.default.classes` and `$gradle.default.classes` in these paths.
     Note that the MUBench Pipeline performs a simple string replacement of these placeholders, to you may specify paths such as `some-project-module/$mvn.default.classes`.

*Hint:* See any of the `version.yml` files of the existing project versions for reference.

##### Compile a Version

The compilation of arbitrary checkouts from a version-control system is, unfortunately, often a hassle and cannot generally be fully automated.
Therefore, for each project version, we manually determine and specify a list of instructions to execute to this end.
Assembling and debugging this list can be a challenge on its own.
The following is a list of things that we found helpful in this process:

* Your compiling on Alpine Linux, the system is at your disposal.
* The instructions are executed *individually* in the project's root directory, so if your want to execute an instruction in a different folder, you need to specify this as one instruction, e.g., `export env=foo && ant compile`.
* When a build instruction fails, it often helps to check the latest MUBench log file to get full error output.
* When a build instruction keeps failing, it often helps to execute it manually on the project version in the MUBench environment, without going through the MUBench Pipeline.
  To this end, open a MUBench Interactive Shell, checkout the project version using the pipeline, go to `checkouts/my-project/v42_4/`, copy the `checkout` folder (which contains the project version), change into the copied folder, and execute your commands.
* When compiling project versions, the MUBench Pipeline tries to capture build dependencies, which it later provides to misuse detectors for analyses, such as type resolution.
  To this end, the pipeline modifies invocations of `mvn` and `gradle`, by adding command line flags or compilation tasks that ensure all build-time dependencies are listed in the command output.
  This sometimes leads to unexpected behaviour, because the command executed is *different* from the command you specify in the instructions list.
* If you need to add some additional file to the project version, in order to make it compile, you can place these files in `data/my-project/versions/v42_5/compile`.
  The content of this folder will be copied into the working directory of the project-version checkout before executing the build instructions.
* An alternative to explicitly compiling the checked-out sources may sometimes be to download and extract a public binary bundle corresponding to the checked-out source code.
  In this case, special care should be taken to ensure that the source code and binaries actually correspond to each other.

#### Add a Misuse

MUBench understands a misuse as an instance of a particular API-usage mistake at a specific source location.
To add a new misuse to the version `v42_5` of the project `myproject` in the dataset:

1. Create a subdirectory in `data/myproject/misuses` and name it after the misuse, say, `data/myproject/misuses/iterator-no-hasnext`.
   The directory name is used as the misuse's Id in the MUBench Dataset, therefore, we recommend choosing a name that is easy to remember and type.
   The name must not contain whitespaces or dots.
2. Create the file `data/myproject/misuses/iterator-no-hasnext/misuse.yml` according to the following schema:

       api:
       - java.util.Collection
       - java.util.Iterator
       internal: false
       description: |
         An element is fetched from an `Iterator` without checking that
         the underlying collection has sufficiently many elements.
       crash: false
       location:
         file: org/my_org/my_project/A.java
         method: m(List, int)
         line: 42
       fix:
         description: Check `hasNext()` before fetching the element.
         commit: https://github.com/my-org/my-project/commit/6296aa33e01e33c81811f0853251c539cdbd61ad
         revision: 6296aa33e01e33c81811f0853251c539cdbd61ad
       violations:
       - missing/condition/value_or_state
       report: https://github.com/my-org/my-project/issues/23
       source:
         name: MUBench Documentation
         url: https://github.com/stg-tud/MUBench/tree/master/data
    
   * The list of API types involved in the misuse (`api`) is used to compute statistics on the diversity of the dataset.
   * The flag indicating whether these types are declared in the project itself or in one of its dependencies (`internal`) is not used at this point.
   * The `description` of the misuse is displayed on the MUBench Review Site to assist in the manual review of detector findings.
   * The flag indicating whether the misuse causes an uncaught exception (`crash`) is used to compute statistics on the severance of API misuses.
   * The `location` of the misuse is used to extract source snippets for display on a MUBench Review Site and to filter detector findings before publishing potential hits for a known misuse to a MUBench Review Site.
     The location is determined by the path of a source `file` relative to one of the source directories specified in the `version.yml` file, a `method` signature (including the method's name and a ', '-separated list of its parameters' simple type names), and (optionally) a line number in this method.
     The line number is used to highlight the misuse location in the source snippet displayed on a MUBench Review Site and to resolve ambiguities, if multiple methods with the same signature occur in the same source file.
   * The `description` of how to `fix` the misuse, the commit Id of the `revision` fixing the misuse (if one exists), and a URL to the commit in a web view (if one exists) are provided on a MUBench Review Site, to assist in the manual review of detector findings.
   * The classification of the misuse according to [the Misuse Classification](http://sven-amann.de/publications/2018-03-A-Systematic-Evalution-of-Static-API-Misuse-Detectors/) (`violations`) is used to compute statistics on the diversity of the dataset.
   * The URL to an issue `report` identifying the misuse is not used at this point.
   * The information about how the misuse was identified (`source`), consisting of a descriptive `name` and a `url` to a resource site are used to compute statistics on how the dataset was assembled.
3. Link the misuse to at least one project version, my adding its Id to the list of misuses in the respective `version.yml` file, e.g., `data/myproject/versions/v42_5/version.yml`:

       ...
       misuses:
       - 'iterator-no-hasnext'
   
4. Create a Java file with a fixed version of the API usage in the misuse and place this file in `data/myproject/misuses/iterator-no-hasnext/correct-usages`.
   This code is provided to the detectors for pattern mining in the experiment to determine an upper bound to the detectors' recall.

*Hint:* See any of the `misuse.yml` files of the existing misuses for reference.

#### Add a Dataset

To conveniently refer to a specific subset of the entire MUBench Dataset, you may define your own data(sub)set in the [datasets.yml](datasets.yml) file, by adding a new dictionary entry with your dataset identifier as its key and a list of the [individual dataset entities](#individual-entities) as its value.
You may reference your dataset using the respective key when [filtering experiment targets](#datasets).

*Hint:* Dataset identifiers are case insensitive.

#### Data Validation

To validate your change, you best load it into MUBench.
To this end, mount the `data/` directory from your working copy of this repository to the MUBench environment by adding `-v /.../data:/mubench/data` to [the Docker command running MUBench](../#setup).

The easiest form of validate is to run `mubench> pipeline check dataset`, which will do syntactical and completeness checks on the dataset files you created.
See `pipeline check -h` for details.

The above validation will not checkout project versions from source control nor try to compile them.
To do so, use the `pipeline checkout` and `pipeline compile` commands.

### Data Issue

Please create a [new issue](https://github.com/stg-tud/MUBench/issues/new) with the following information:

* A short description of the misuse and its fix.
* Instructions how to checkout and compile the project with the misuse from version control.
* The exact location of the misuse in the project's source code (file, class, and method).
* (Optional) A link to an issue report that uncovered the misuse.
