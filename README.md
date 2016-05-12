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

(Other version might work, but where not tested)

### Setup

1. [Download PyYAML](http://pyyaml.org/wiki/PyYAML) to somewhere on your machine.
2. Unzip the package and install with `python setup.py install`.
3. Run `scripts/verify.py` to check correct setup.

### Scripts

Run any of the scripts in `scripts`. See script headers for details.

### Benchmark

MUBench is a benchmark for API-misuse detectors. Run `python benchmark.py -h` for details about how to benchmark detectors.

MUBench uses the misuses specified in the `data` subfolder. The first time a misuse is used in benchmarking, the repository containing that misuse is cloned. Subsequently, the existing clone is used, such that benchmarking runs offline.

## Benchmark Your Detector

To benchmark your own detector the following steps are necessary:   

1. Create a new subfolder `my-detector` in the [detectors](https://github.com/stg-tud/MUBench/tree/master/detectors) folder. `my-detector` will be the Id used to refer to your detector when running the benchmark.
2. Create a `my-detector/my-detector.cfg`. Add a `DEFAULT` section to the file and set the `Result File` key to the name of the file your detector will write its findings to. See our example configuration for details: [dummy-detector.cfg](https://github.com/stg-tud/MUBench/blob/master/detectors/dummy-detector/dummy-detector.cfg).
3. Add an executable JAR with your detector as `my-detector/my-detector.jar`. When running MUBench, this JAR will be invoked with the arguments and is expected to write the outputs described below.
4. Run MUBench
5. Manually review the results.

*Which Inputs Will I Get?*

All inputs are passed to the JAR as command-line arguments.
- args[0]: The path to the project containing the misuse. You may use this to mine usage patterns and find misuses.
- args[1]: The file MUBench expects you to write your findings to. This file is `results/my-detector/<misuse>/findings.txt`.
- args[2]: (Optional) The path to a `.pattern` file, which contains the fixed version of the usage MUBench expects your detector to find in the project. The file contains a Java Source Code snippet. For examples see the `*.pattern` files in [`data`](https://github.com/stg-tud/MUBench/tree/master/data).

*What Should My Output File Look Like?*

MUBench expects you findings in the [YAML](http://yaml.org/) format. The benchmark reads the two keys `file` (the path to a file your detector found a misuse in) and `graph` (a DOT graph describing the misuse your detector found in that file). You can provide both or only one of the keys per finding. Providing a DOT graph helps MUBench filter false positives and, thereby, reduce the review effort you have to invest later.

Example output file:
```
file: commons/proper/lang/trunk/src/java/org/apache/commons/lang/text/StrBuilder.java
graph: >
	digraph {
	  0 [label="StrBuilder#this#getNullText"]
	  1 [label="String#str#length"]
	  0 -> 1
	}
---
file: src/com/google/javascript/rhino/jstype/UnionType.java
graph: >
	digraph {
	  0 [label="UnionTypeBuilder#builder#build"]
	  1 [label="IF#IF#CONTROL"]
	  0 -> 1
	}
```

## Contribute

To contribute to MUBench, simply use our meta-data template below to describe the API misuse you discovered and [create a new file in the `data` folder](https://github.com/stg-tud/MUBench/new/master/data) named `<project>.<issue>.yml`, where <project> must be unique for the repository. You can also create a file locally and submit it via GitHub's drag&drop feature or fork this repository and send a pull request after you committed new misuses.

To make it even easier, you can also simply [fill our online survey](http://goo.gl/forms/3hua7LOFVJ) to submit your finding.

```
source:
  name: Foo
  url:  https://foo.com
project:
  name: A
  url:  http://a.com
report: http://a.com/issues/42
description: >
  Client uses T1.foo() before T2.bar().
crash:    yes|no
internal: yes|no
api:
  - qualified.library.identifier.T1
  - qualified.library.identifier.T2
characteristics:
  - superfluous call
  - missing call
  - wrong call
  - wrong call order
  - missing precondition/predicate
  - missing precondition/null
  - missing precondition/parameter constraint
  - missing catch
  - missing finally
  - ignored result
pattern:
  - single node
  - single object
  - multiple objects
challenges:
  - multi-method
  - multiple usages
  - path dependent
fix:
  description: >
    Fix like so...
  commit: http://a.com/repo/commits/4711
  files:
    - name: src/main/java/a/Client.java
      diff: http://a.com/repo/commits/4711/Client.java
```

## License

[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)
