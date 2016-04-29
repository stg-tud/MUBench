<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : A Benchmark for API-Misuse Detectors

The MUBench dataset is an [MSR 2016 Data Showcase](http://2016.msrconf.org/#/data). Please feel free to [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann), if you have any questions.

## Contributors

* [Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) (Project Lead)
* [Sarah Nadi](http://www.sarahnadi.org/)
* Hoan A. Nguyen
* [Tien N. Nguyen](http://home.eng.iastate.edu/~tien/)

## Publications

* ['*MUBench: A Benchmark of API-Misuse Detectors*'](http://sven-amann.de/publications/#ANNNM16)

## Run Scripts

1. [Download PyYAML](http://pyyaml.org/wiki/PyYAML) to somewhere on your machine.
2. Unzip the package and install with `python setup.py install`.
3. Run `scripts/verify.py` to check correct setup.
4. Run the script of your choice (see file header for documentation).

## MUBenchmark

The MUBenchmark is a benchmark for usage model miners and misuse detectors  
Note: MUBenchmark relies on relative paths. You may move the complete MUBench folder anywhere, but removing parts of its content might make the benchmark unusable.  

###### Setup
1. Follow the instructions in the section Run Scripts to install PyYAML  
2. Install git , svn, and java  
   (Note: MUBenchmark was only tested with the following versions:  
          java version 1.8.0_66, git version 2.6.0, svn version 1.9.3)  
3. Run `benchmark/mubenchmark.py check` to check correct setup  

###### Run the Benchmark
MUBenchmark consists of several subprocesses.  
To see a list of available subprocesses, you may use `benchmark/mubenchmark.py -h`.  
For more detail about how to use a specific subprocess, you may use `benchmark/mubenchmark.py <subprocess> -h`.

The following subprocesses are available:
* `check`  
usage: `MUBenchmark check [-h]`  
example: `py benchmark/mubenchmark.py check`  
This subprocess can be used to validate if all prerequisites to run the benchmark are met.  

* `checkout`  
usage: `MUBenchmark checkout [-h]`  
example: `py benchmark/mubenchmark.py checkout`  
This subprocess can be used to pre-load all projects used by the benchmark.  
The projects will be loaded into the `MUBenchmark-checkouts` folder. This is not configurable to keep MUBenchmark self-contained.  

* `mine`  
usage: `MUBenchmark mine [-h]`  
example: `py benchmark/mubenchmark.py mine`  
This subprocess is not yet implemented.  

* `eval`  
usage: `MUBenchmark eval [-h] [--only X [X ...]] [--ignore Y [Y ...]] [--timeout s] detector`  
example: `py benchmark/mubenchmark.py eval dummy-miner --only aclang acmath adempiere --ignore acmath.998-2 --timeout 600`  
This subprocess expects an identifier for the detector to run. Consider [`detectors`](https://github.com/stg-tud/MUBench/tree/master/detectors) for available detectors. Each subfolder of `/detectors` is a valid identifier.  
Note that this also expects the detector to run on complete projects, hence it needs to generate its own usage models. This will probably be changed in the future to have a clean split between mine and eval.  
This subprocess will implicitly load all projects into the `MUBenchmark-checkouts` folder.  

Optional arguments:  
`--only X [X ...]`	allows you to run the detector only on all MUBench data files (see [`data`](https://github.com/stg-tud/MUBench/tree/master/data)) which contain any one of the given strings  
`--ignore Y [Y ...]`	will let the benchmark ignore all MUBench data files (see [`data`](https://github.com/stg-tud/MUBench/tree/master/data)) which contain any one of the given strings  
`--timeout s`			will set a timeout (in seconds) for the misuse detector; cases where a timeout occurred will be ignored in the evaluation  


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
