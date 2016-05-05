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
* ['*The Misuse Classification*'](http://www.st.informatik.tu-darmstadt.de/artifacts/muc/)

## Run Scripts

1. [Download PyYAML](http://pyyaml.org/wiki/PyYAML) to somewhere on your machine.
2. Unzip the package and install with `python setup.py install`.
3. Run `scripts/verify.py` to check correct setup.
4. Run the script of your choice (see file header for documentation).

## MUBench benchmark

The MUBench benchmark is a benchmark for usage model miners and misuse detectors  
Note: MUBenchmark relies on relative paths. You may move the complete MUBench folder anywhere, but removing parts of its content might make the benchmark unusable.  

###### Setup
1. Follow the instructions in the section Run Scripts to install PyYAML    
2. Install git , svn, and java  
   (Note: MUBenchmark was only tested with the following versions: java version 1.8.0_66, git version 2.6.0, svn version 1.9.3)  
3. Run `mubenchmark.py check` to check correct setup  

###### Run the Benchmark
The benchmark consists of several subprocesses.  
To see a list of available subprocesses, you may use `py benchmark.py -h`.  
For more detail about how to use a specific subprocess, you may use `py benchmark.py <subprocess> -h`.

###### Contribute to the Benchmark
To benchmark your own detector the following steps are necessary:   
1. Create a new subfolder in the [detectors](https://github.com/stg-tud/MUBench/tree/master/detectors) folder.   
   The name of this subfolder will be the ID of your detector in the benchmark. From now on, we refer to it as `<your-detector>`.   
2. In your new subfolder, create a `<your-detector>.cfg` file. This file will contain everything which is specific to your detector.   
   You may refer to the [dummy-detector.cfg](https://github.com/stg-tud/MUBench/blob/master/detectors/dummy-detector/dummy-detector.cfg) for formatting.   
   We expect a `DEFAULT` section, containg the key `Result File`, which is the name of the file you will write your results into.   
3. Add your detector as `<your-detector>.jar` to your subfolder.

__Which inputs will you get?__   
All inputs are passed through the args array:   
- args[0]:	The path to the project root. This may be used by your miner to find patterns.
- args[1]:	The path to a `.pattern` file. These files contain a java code snippet of the misuse. You may use this file if you want to benchmark your misuse detection without relying on pattern mining.
- args[2]:	Your output folder. For the benchmark to evaluate your results correctly you must write the result file given in your config into this folder. If you want to manually check your results you will find them in the `results/<your-detector>` subfolder.

__What should your result file look like?__
If you want to evaluate your results using `py benchmark.py eval <your-detector>` after running the `detect` subprocess we expect the following format in your result file:   
- `File: <file-with-misuse>` lines:	this option only makes sense if you can't output more specific information and is only considered if no other information is given. You will probably have to manually check the positive results after the evaluation.
- DOT graphs:	you may add graphs in the DOT format to your result file. The benchmark will compare all labels mentioned in your graphs to the misuse graph in our data. This will lead to more precise results but we still recommend manually checking the positive results.

Example DOT graph:
```
digraph {
  0 [label="StrBuilder#this#getNullText"]
  1 [label="String#str#length"]
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
