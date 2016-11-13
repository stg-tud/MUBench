<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : A Benchmark for API-Misuse Detectors

The MUBench dataset is an [MSR 2016 Data Showcase](http://2016.msrconf.org/#/data). Please feel free to [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann), if you have any questions.

MuBench CI Status: [![MuBench CI Status](https://api.shippable.com/projects/570d22d52a8192902e1bfa79/badge?branch=master)](https://app.shippable.com/projects/570d22d52a8192902e1bfa79)

## Contributors

* [Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) (Project Lead)
* [Sarah Nadi](http://www.sarahnadi.org/)
* Hoan A. Nguyen
* [Tien N. Nguyen](http://home.eng.iastate.edu/~tien/)
* [Mattis Kämmerer](https://github.com/M8is)
* [Jonas Schlitzer](https://github.com/joschli)

## Publications

* ['*MUBench: A Benchmark of API-Misuse Detectors*'](http://sven-amann.de/publications/#ANNNM16)
* ['*The Misuse Classification*'](http://www.st.informatik.tu-darmstadt.de/artifacts/muc/)

## Run MUBench

### Setup

1. Install [Docker](https://www.docker.com/products/overview#/install_the_platform).
2. When on Windows, you need to allow Docker to mount your MUBench-checkout directory:
  1. Right click the Docker icon in the system tray and choose "Settings".
  2. Open the "Shared Drives" tab.
  3. Ensure the drive that contains your checkout is selected and apply.
3. Run `./mubench check` (or `./mubench.bat check`). On the first run, this may take some time.

### Benchmark

MUBench is a benchmark for API-misuse detectors. Run `./mubench -h` for details about how to benchmark detectors.

MUBench uses the misuses specified in the `data` subfolder. The first time a misuse is used in benchmarking, the repository containing that misuse is cloned. Subsequently, the existing clone is used, such that benchmarking runs offline.

## Benchmark Your Detector

To benchmark your own detector the following steps are necessary:   

1. Create a new subfolder `my-detector` in the [detectors](https://github.com/stg-tud/MUBench/tree/master/detectors) folder. `my-detector` will be the Id used to refer to your detector when running the benchmark.
2. Add an executable JAR with your detector as `my-detector/my-detector.jar`.<sup>[1](#mubenchcli)</sup>
3. Run MUBench
4. Review the results.
5. Let MUBench summarize the results.

<a name="mubenchcli">1</a>: Your detector jar's entry point is expected to be a [MUBench Runner](#runner).

### <a name="runner" /> MUBench Runner

For MUBench to run your detector and interpret its results, your detector's executable needs to comply with MUBench's command-line interface. The easiest way to achieve this is for your entry-point class to extend `MuBenchRunner`, which comes with the Maven dependency [`de.tu-darmstadt.stg:mubench.cli`](https://github.com/stg-tud/MUBench/tree/master/benchmark/mubench.cli) via our repository at `http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/`.

A typical MUBench Runner looks like this:

    public class XYRunner extends MuBenchRunner {
      public static void main(String[] args) {
        new XYRunner().run(args);
      }
      
      void detectOnly(CodePath patternPath, CodePath targetPath, DetectorOutput output) throws Exception {
        ...
      }
      
      void mineAndDetect(CodePath trainingAndTargetPath, DetectorOutput output) throws Exception {
        ...
      }
    }

Currently, Runners should support two run modes:

1. "Detect Only"-mode, where the detector is provided with hand-crafted patterns (a one-method class implementing the correct usage) and some target code to find violations of these patterns in. All input is provided as Java source code and corresponding Bytecode.
2. "Mine and Detect"-mode, where the detector should mine its own patterns in the provided code base and find violations in that same code base. Again, input is provided as source code and corresponding Bytecode.

The `DetectorOutput` is essentially a collection where you add your detector's findings.

### How do I review?

We are currently rebuilding the review infrastructure. Please come back for more details in a bit!

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
## Setup Mubench Webserver

Requirements: php5.6, mysql5.6

PHP Extensions: php5.6xml, php5.6mbstring

1. Run the `docker run --rm -v "PATH/TO/php_backend":/mubench svamann/mubench-ci composer install` in the php_backend directory
2. Create upload directory in php_backend
3. Set your database credentials in settings.php
3. Upload the php_backend directory
  1. Mount it with your apache
  2. Give read/write permissions on the upload and logs directory
5. Create metadata and patterns table in your mysql database with:

```
CREATE TABLE metadata (
misuse TEXT NOT NULL,
description TEXT NOT NULL,
fix_description TEXT NOT NULL,
violation_types TEXT NOT NULL,
file TEXT NOT NULL,
method TEXT NOT NULL,
code TEXT NOT NULL,
);

CREATE TABLE patterns (
misuse TEXT NOT NULL,
name TEXT NOT NULL,
code TEXT NOT NULL
);

CREATE TABLE stats (
id TEXT NOT NULL, 
result TEXT NOT NULL, 
runtime TEXT NOT NULL, 
number_of_findings TEXT NOT NULL
);
```

## License

[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)
