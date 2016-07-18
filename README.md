<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : A Benchmark for API-Misuse Detectors

The MUBench dataset is an [MSR 2016 Data Showcase](http://2016.msrconf.org/#/data). Please feel free to [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann), if you have any questions.

## Contributors

* [Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) (Project Lead)
* [Sarah Nadi](http://www.sarahnadi.org/)
* Hoan A. Nguyen
* [Tien N. Nguyen](http://home.eng.iastate.edu/~tien/)
* [Mattis Kämmerer](https://github.com/M8is)

## Publications

* ['*MUBench: A Benchmark of API-Misuse Detectors*'](http://sven-amann.de/publications/#ANNNM16)
* ['*The Misuse Classification*'](http://www.st.informatik.tu-darmstadt.de/artifacts/muc/)

## Run MUBench

### Requirements

* Python 3.x
* Java 8
* git 2.x
* svn 1.8+
* Gradle 1.10+
* Maven 3.3.x

(Other version might work, but where not tested)

### Setup

1. `pip install pyyaml`
3. Run `./mubench check` to check requirements.

### Benchmark

MUBench is a benchmark for API-misuse detectors. Run `./mubench -h` for details about how to benchmark detectors.

MUBench uses the misuses specified in the `data` subfolder. The first time a misuse is used in benchmarking, the repository containing that misuse is cloned. Subsequently, the existing clone is used, such that benchmarking runs offline.

## Benchmark Your Detector

To benchmark your own detector the following steps are necessary:   

1. Create a new subfolder `my-detector` in the [detectors](https://github.com/stg-tud/MUBench/tree/master/detectors) folder. `my-detector` will be the Id used to refer to your detector when running the benchmark.
2. Add an executable JAR with your detector as `my-detector/my-detector.jar`.<sup>[1](#mubenchcli)</sup>
3. Run MUBench
4. Manually review the results.
5. Let MUBench summarize the results.

<a name="mubenchcli">1</a>: Your detector jar's entry point is expected to be what we call a MUBench Runner. It receives input and is expected to write output that the benchmark understands. We provide you some utilities to do so via `mubench.cli`, which comes as a Maven dependency `de.tu-darmstadt.stg:mubench.cli:0.0.3-SNAPSHOT` (Attention: `mubench.cli` is currently not hosted in a public Maven repository. Please find the project [in this repository](https://github.com/stg-tud/MUBench/tree/master/benchmark/mubench.cli) and build it yourself).

### Which Inputs Will I Get?

Use `de.tu_darmstadt.stg.mubench.cli.ArgParser.parse(String[] args)` to parse the command-line arguments to an instance of `de.tu_darmstadt.stg.mubench.cli.DetectorArgs`. This gives you access to the following paths:

- `getFindingsFile()`: The file MUBench expects you to write your findings to.
- `getProjectSrcPath()`: The path to the project sources containing the misuse. You may use this to mine usage patterns and find misuses.
- `getProjectClassPath()`: The class files corresponding to the project sources.
- `getPatternsSrcPath()`: The path to the pattern files. Pattern files are regular java files containing a class with one or more methods, each containing a correct usage for the misuses in the project.
- `getPatternsClassPath()`: The class files corresponding to the pattern sources.

Note that the getters check that the provided values are valid and throw if otherwise. This way, MUBench can report a meaningful error, should one of the parameters somehow be wrong.

### What Output Should I Produce?

Use `de.tu_darmstadt.stg.mubench.cli.DetectorOutput` to collect and write your output. Add one or more instances of `de.tu_darmstadt.stg.mubench.cli.DetectorFinding` to the output. Each finding corresponds to one misuse your detector finds in a project. For each you must provide two properties that MUBench uses to identify potential hits for the known misuses:

- `file`: The full path to either source or class file your detector found the misuse in.
- `method`: either the method's simple name (e.g., `method`) or a full signature (e.g., `method(Object, List, int)`) of the method your detector found the misuse in. If you provide a full signature and MUBench is unable to identify a potential hit, it automatically falls back to using only the method name. This way it ensures that a difference in the signature notation does not make us miss a potential hit.

You may provide the finding with additional properties that help reviewing your detector's findings. These properties will be included in the review information.

### How do I review?

MUBench prepares a review website for you, which lists the potential hits for all misuses in its dataset. After running the review preparation, you can open this site from `reviews/index.html`. Follow the links to the review-details pages to review the potential hits of your detector. The pages list for every misuse the potential hits, with an `Id` and all the metadata your detector provides in the output.

To report an actual hit of your detector, create `reviews/<detector>/<project>/<version>/<misuse>/reviewX.yml` with `X` being 1 or 2, depending on whether you are the first or second reviewer. The files content should look like follows:

```
reviewer: Sven
hits:
  - id: <potential-hit-id>
    elements:
      - missing/call
  - id: <other-potential-hit-id>
    elements:
      - missing/condition/null_check
      - superfluous/call
comment: >
  This is especially interesting, because...
```

When you're done reviewing all potential hits, tell MUBench to summarize the results for you.

## Contribute Misuses

To contribute to MUBench, simply use our meta-data template below to describe the API misuse you discovered and send it to [Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann).

```
source:
  name: Foo
  url:  https://foo.com
project:
  name: A
  url:  http://a.com
  repository: http://a.com/repo/a.git
report: http://a.com/issues/42
description: >
  Client uses T1.foo() before T2.bar().
location:
  revision: 4710
  file: a/Client.java
  method: m(Foo, int)
crash:    yes|no
internal: yes|no
api:
  - qualified.library.identifier.T1
  - qualified.library.identifier.T2
characteristics:
  - missing/call
  - misplaced/call
  - superfluous/call
  - missing/condition/null_check
  - missing/condition/value_or_state
  - missing/condition/threading
  - missing/condition/environment
  - superfluous/condition
  - missing/exception_handling
  - superfluous/exception_handling
  - missing/guarantee
build:
  src: src/main/java
  commands:
    - mvn compile
  classes: target/classes
fix:
  description: >
    Fix like so...
  commit: http://a.com/repo/commits/4711
  revision: 4711
  files:
    - name: a/Client.java
      diff: http://a.com/repo/commits/4711/Client.java
```

## License

[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)
