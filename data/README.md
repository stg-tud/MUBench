<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Dataset

The MUBench Dataset references projects with known API misuses. Each subfolder of this directory identifies one project. For each project, the dataset references one or more project versions that contain the known misuses (usually the version immediately before a particular misuse was fixed). The dataset also specifies the misuses themselves and links misuses and project versions.

When running experiments you may use the qualified project, version, or misuse ids to select particular datapoints for your experiment. The project id is the name of the respective subfolder in this directory. The qualified version id has the form `<project-id>.<version-id>`, where the version id is the name of the respective directory in `<project-id>/versions/`. The qualified misuse id has the form `<project-id>.<misuse-id>`, where the misuse id is the name of the respective directory in `<project-id>/misuses/`.

You may also use qualified project, version, or misuse ids to specify sub-dataset in [datasets.yml](datasets.yml), to conveniently run experiments on certain subsets of the entire dataset.

## Statistics

The current dataset contains 209 misuses from 108 project versions of 50 projects.
It contains 162 misuses in 47 compilable project versions of 25 projects.
It contains 64 misuses with corresponding crafted examples of correct usage, 39 from 29 compilable versions of 13 projects and 25 hand-crafted examples.

**Manually Collected:**

* 25 misuses from a developer survey
* 24 misuses from manual review of [the BugClassify dataset](https://www.st.cs.uni-saarland.de/softevo/bugclassify/)
* 17 misuses from manual review of [the Defects4J dataset](https://github.com/rjust/defects4j)
* 16 misuses from manual review of the QACrashFix dataset (became unavailable)
* 11 misuses from manual review of commits changing `javax.crypto.Cipher` usages on Sourceforge
* 3 misuses from manual review of commits changing `javax.crypto.Cipher` usages on GitHub
* 3 misuses from "Analyse der Verwendung von Kryptographie-APIs in Java-basierten Anwendungen", Ziegler, Master's Thesis, Uni Bremen, Germany
* 2 misuses from API-usage constraints reported in ["What should developers be aware of?", Monperrus et al., Empirical Software Engineering '12](https://arxiv.org/abs/1205.6363)
* 1 misuses from manual review of [the iBugs dataset](https://www.st.cs.uni-saarland.de/ibugs/)

**Identified by API-Misuse Detectors:**

* 77 misuses from 18 versions of 12 projects; source: ["How Good are the Specs? A Study of the Bug-Finding Effectiveness of Existing Java API Specifications", Owolabi et al., ASE'16](http://fsl.cs.illinois.edu/spec-eval/)
* 9 Pradel
* 8 DMMC
* 7 MUDetect
* 4 Tikanga
* 2 Jadet

### ICSE 18

*Total*: 132 misuses total, 85 misuses in compilable project versions

*Experiment 1*: 64 misuses, 39 from 29 versions of 13 projects and 25 hand-crafted examples

*Experiment 2*: 5 projects, 7 previously-unknown misuses identified in the MUDetect's top-20 findings

*Experiment 3*: 85 misuses, 60 from 29 versions of 13 projects and 25 hand-crafted examples

### TSE 17

*Total*: 125 misuses total, 78 misuses in compilable project versions

*Experiment 1*: 64 misuses, 39 from 29 versions of 13 projects and 25 hand-crafted examples

*Experiment 2*: 5 projects, 14 previously-unknown misuses identified in the detectors' top-20 findings

*Experiment 3*: 53 misuses from 29 versions of 13 projects (no hand-crafted examples)

## Contribute

To contribute to the MUBench Dataset, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) with details about the misuses. For each misuse, please try to provide

* A description of the misuse (and its fix).
* A link to the website of the project you found the misuse in.
* A link to the project's publicly-readable version-control system, and a commit id to a version with the misuse or, ideally, to the commit that fixes the misuse.
* The misuse's location (file, method, and misused API).
* Instructions on how to compile the project in the respective version.
