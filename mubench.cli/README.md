<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Detector Interface

Setting up your own detector for evaluation in MUBench is simple:

1. Implement a [MUBench Runner](#runner) for your detector.
2. Place an executable JAR with your runner as its entry point in `detectors/mydetector/mydetector.jar`.
3. Create [/detectors/mydetector/releases.yml](#list-of-detector-releases), to provide version information.
4. Create [/detectors/mydetector/detector.py](#detector.py), to post process your detector's findings.
5. [Run Benchmarking Experiments](../mubench.pipeline/) using `mydetector` as the detector id.

If you have a detector set up for running on MUBench, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) to publish it with the benchmark. Feel free to do so as well, if you have questions or require assistance.

## Runner

To interface with MUBench, all you need is to implement the `MuBenchRunner` interface, which comes with the Maven dependency `de.tu-darmstadt.stg:mubench.cli` via our repository at http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/ (check [the pom.xml](pom.xml) for the most-recent version).

A typical runner looks like this:

```java
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
```

It supports two run modes:

1. "Detect Only" (Experiment 1), where the detector is provided with hand-crafted correct usages (a one-method class implementing the correct usage) and some target code to find violations of these correct_usages in.
2. "Mine and Detect" (Experiment 2/3), where the detector should mine its own patterns in the provided codebase and find violations in that same codebase.

In either mode, the `DetectorArgs` provide all input as both the Java source code and the corresponding Bytecode. Additionally, it provides the classpath of all the code's dependencies.

The `DetectorOutput` is essentially a collection where you add your detector's findings, specifying their file and method location and any other property that may assist manuel reviews of the findings. MUBench expects you to add the findings ordered by the detector's confidence, descending. You may also output general statistics about the detector run.

## Releases.yml

This file must be at `detectors/mydetector/releases.yml` and contain a list of releases of your detector.

Entries look like this:

```yaml
- cli-version: 0.0.10
  md5: 2470067fac02ee118b7d49287246e20a
- cli-version: 0.0.8
  md5: 9e5252816faecf552464f0a6abde714f
  tag: my-tag
```

The must contain at least one entry. By default, MUBench uses the newest version listed. Each entry consists of the following keys:

* `cli-version` - The [MUBench Runner](#runner) version implemented by the respective detector release. This information is used to invoke your detector.
* `md5` (Optional) - The MD5 hash of the `detector/mydetector/mydetector.jar` file. MUBench will use this value to check the integrity of the detector, if it is loaded from the remote detector registry. The MD5 is mandatory in this case.
* `tag` (Optional) - Used to reference specific detector releases. To request a specific detector release, add `--tag my-tag` to the MuBench command. Note that tags are case insensitive, i.e., `Foo` and `foo` are the same tag.

## Detector.py

To post process your detector's results, you need to create `detectors/mydetector/mydetector.py` with a class `mydetector`, which implements [`data.detector.Detector`](https://github.com/stg-tud/MUBench/blob/master/mubench.pipeline/data/detector.py) with the method `_specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding`. A specialized finding prepares a finding of a detector for display on the review page, for example, by converting dot graphs to images. The [`data.detector_specialising.specialising_util`](https://github.com/stg-tud/MUBench/blob/master/mubench.pipeline/data/detector_specialising/specialising_util.py) module contains utilities for this purpose.

Here is an example of a basic implementation which does no post processing:

```python
from data.detector import Detector
from data.finding import Finding, SpecializedFinding

class MyDetector(Detector):
    def _specialize_finding(self, findings_path: str, finding: Finding) -> SpecializedFinding:
        return SpecializedFinding(finding)
```

Consider [MuDetect.py](https://github.com/stg-tud/MUBench/blob/master/detectors/MuDetect/MuDetect.py) for a more advanced example with post processing.

## Debugging

When debugging your detector, there's no need to package and integrate it into MUBench after every change. You can invoke your runner directly from your IDE instead, which is much more convenient. To this end, just follow these steps:

1. Run `./mubench detect DemoDetector E --only P`, where `E` is [the experiment](../mubench.pipeline#experiments) you want to debug your detector in and `P` is [the project or project version](../data) that you want to debug your detector on, e.g., `aclang`.
2. Once this finished, open the newest log file in `./logs` and look for a line from `detect.run` saying something like `Executing 'java -jar DemoDetector.jar ...'`.
3. Copy the command-line parameter of this Java invokation (the `...` above).
4. Invoke your runner implementation with these parameters from your IDE.
5. Happy debugging.
