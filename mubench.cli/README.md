<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Detector Interface

Setting up your own detector for evaluation in MUBench is simple:

1. [Implement a MUBench Runner](#implement-a-mubench-runner) for your detector.
2. Place an executable JAR with your runner at `detectors/<mydetector>/latest/<mydetector>.jar`.
3. Add [detector version and CLI version information](#provide-version-information) to `/detectors/<mydetector>/releases.yml`.
4. [Run benchmarking experiments](../mubench.pipeline/) using `<mydetector>` as the detector id.

If you have a detector set up for running on MUBench, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) to publish it with the benchmark.
Feel free to do so as well, if you have questions or require assistance.


## Implement a MUBench Runner

To run your detector in MUBench experiments, you need to configure a MUBench Runner that invokes your detector and reports its findings to [the MUBench Pipeline](../mubench.pipeline).
We provide infrastructure for implementing runners in the Maven dependency `de.tu-darmstadt.stg:mubench.cli` via our repository

    http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/

Check the [MUBench CLI documentation](http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/cli/) for details on how to implement runners and other utilities available through this dependency.

Once you configured the runner, you need to bundle it together with your detector into an executable Jar. This Jar must have the runner as its entry point.
See the configuration of the `maven-assembly-plugin` in [the `pom.xml` file](./pom.xml) for an example of how we do this for our `DemoDetector`.


## Provide Version Information

Each detector has a `release.yml` file that provides version information.
The most-simple version of such a file, which suffices to run a detector locally, might look as follows:

```yaml
- cli-version: 0.0.13
  md5: foo
```

* The `cli-version` names the version of the `mubench.cli` dependency used to implement the respective [MUBench Runner](#implement-a-mubench-runner).
* The `md5` might be any string.
  When running experiments, [the MUBench Pipeline](../mubench.pipeline) uses this string only to determine whether the detector changed (by checking whether the `md5` changed) and to invalidate existing results accordingly.
  Only when the detector is integrated into the MUBench detector repository, such that [the MUBench Pipeline](../mubench.pipeline) can download it automatically, the `md5` needs to be changed to the actual hash of the Jar file, for download verification.

It is possible to manage multiple versions of a detector via the `release.yml` file.
The file might then look as follows:

```yaml
- cli-version: 0.0.10
  md5: 2470067fac02ee118b7d49287246e20a
- cli-version: 0.0.8
  md5: 9e5252816faecf552464f0a6abde714f
  tag: my-tag
```

* The `cli-version` names the version of the `mubench.cli` dependency used to implement the respective [MUBench Runner](#implement-a-mubench-runner).
* The `md5` is the hash of the respective Jar file.
* The `tag` is an identifier for the detector version (case insensitive).
  You may specify this identifier when running experiments, using the `--tag` option.
  If the `--tag` option is not specified, [the MUBench Pipeline](../mubench.pipeline) runs the top-most detector version listed in the `release.yml` file.
  If this detector version has no `tag`, `latest` is used as the default.
  In any case, [the MUBench Pipeline](../mubench.pipeline) expects the respective Jar file at `detectors/<mydetector>/<tag>/<mydetector>.jar`.


## Debugging

To debug a [MUBench Runner](#implement-a-mubench-runner) it is more convenient to run it directly from an IDE, instead of bundling an executable Jar to run it in MUBench after every change.
To do this, proceed as follows:

1. Run `./mubench run <E> <mydetector> --only <P>`, where `<E>` is [the experiment](../mubench.pipeline/#experiments) you want to debug and `P` is [the project or project version](../data/#filtering) you want to debug with, e.g., `aclang`.
2. Abort this run, as soon as the detector was started.
3. Open the newest log file in `./logs` and look for a line saying something like `Executing 'java -jar <mydetector>.jar ...'`.
3. Copy the command-line parameters of this Java invocation (the `...` above).
4. Invoke your runner's `main()` method with these parameters from your IDE.
