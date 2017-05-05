<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Detector Interface

Setting up your own detector for evaluation in MUBench is simple:

1. Implement a [MUBench Runner](#runner) for your detector.
2. Place an executable JAR with your runner as its entry point in `detectors/my-detector/my-detector.jar`.
3. Optionally create `detectors/my-detector/my-detector.py` for any post processing on the detector findings (see the other detectors for examples).
4. [Run Benchmarking Experiments](../mubench.pipeline/) using `my-detector` as the detector id.

If you have a detector set up for running on MUBench, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) to publish it with the benchmark. Feel free to do so as well, if you have questions or require assistance.

## Runner

To interface with MUBench, all you need to implement the `MuBenchRunner` interface, which comes with the Maven dependency `de.tu-darmstadt.stg:mubench.cli` via our repository at http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/ (check [the pom.xml](pom.xml) for the most-recent version).

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
