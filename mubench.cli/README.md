<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Detector Interface

Setting up your own detector for evaluation in MUBench is simple:

1. Implement a [MUBench Runner](#runner) for your detector.
2. Place an executable JAR with your runner as its entry point in `detectors/my-detector/my-detector.jar`.
3. Create a [/detectors/my-detector/releases.yml](#list-of-detector-releases), to provide version information.
4. Create a [/detectors/my-detector/detector.py](#detector.py) for any post processing on the detector findings.
5. [Run Benchmarking Experiments](../mubench.pipeline/) using `my-detector` as the detector id.

If you have a detector set up for running on MUBench, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) to publish it with the benchmark. Feel free to do so as well, if you have questions or require assistance.

## Runner

To interface with MUBench, all you need is to implement the `MuBenchRunner` interface, which comes with the Maven dependency `de.tu-darmstadt.stg:mubench.cli` via our repository at http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/ (check [the pom.xml](pom.xml) for the most-recent version).

A typical runner looks like this:

    public class MyRunner extends MuBenchRunner {
      public static void main(String[] args) {
        new MyRunner().run(args);
      }

      @Override
      protected void detectOnly(DetectorArgs args, DetectorOutput output) throws Exception {
        // Run detector in Experiment 1 configuration...
      }

      @Override
      protected void mineAndDetect(DetectorArgs args, DetectorOutput output) throws Exception {
        // Run detector in Experiment 2/3 configuration...
      }
    }

It supports two run modes:

1. "Detect Only" (Experiment 1), where the detector is provided with hand-crafted patterns (a one-method class implementing the correct usage) and some target code to find violations of these patterns in.
2. "Mine and Detect" (Experiment 2/3), where the detector should mine its own patterns in the provided codebase and find violations in that same codebase.

In either mode, the `DetectorArgs` provide all input as both the Java source code and the corresponding Bytecode. Additionally, it provides the classpath of all the code's dependencies.

The `DetectorOutput` is essentially a collection where you add your detector's findings, specifying their file and method location and any other property that may assist manuel reviews of the findings. MUBench expects you to add the findings ordered by the detector's confidence, descending. You may also output general statistics about the detector run.

## Releases.yml

This file must be at `detectors/my-detector/releases.yml` and contain a list of releases of your detector.

Entries look like this:

    - cli-version: 0.0.10
      md5: 2470067fac02ee118b7d49287246e20a
    - tag: my-tag
      cli-version: 0.0.8
      md5: 9e5252816faecf552464f0a6abde714f

The must contain at least one entry. By default, MUBench uses the newest version listed.

`cli-version` is the [MUBench Runner](#runner) version implemented by the respective detector release. This information is used to invoke your detector.

`md5` is the md5 hash of the `detector/my-detector/my-detector.jar` file. MUBench will use this value to check the integrity of the detector if it was loaded from a remote source.

`tag` is optional and can be used to reference specific detector releases. To request a specific detector release, add `--tag my-tag` to the MuBench command.

## Detector.py

To post process your detector's results, you need to create `detectors/my-detector/my-detector.py`. This script should implement a subclass of [`data.detector.Detector`](https://github.com/stg-tud/MUBench/blob/master/mubench.pipeline/data/detector.py), which must define `_specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding`. A specialized finding is supposed to convert the output of the detector to human-readable output, which will be displayed on the review page. The [`data.detector_specialising.specialising_util`](https://github.com/stg-tud/MUBench/blob/master/mubench.pipeline/data/detector_specialising/specialising_util.py) module contains utilities for this purpose.

Here is an example of a basic implementation which does no post processing:

    from data.detector import Detector
    from data.finding import Finding, SpecializedFinding

    class MyDetector(Detector):
        def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
            return SpecializedFinding(finding)

Consider [MuDetect.py](https://github.com/stg-tud/MUBench/blob/master/detectors/MuDetect/MuDetect.py) for a more advanced example with post processing.
