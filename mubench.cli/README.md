<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Detector Interface

If you want to integrate your detector into MUBench, please follow these steps:

1. [Implement a MUBench Runner](#implement-a-mubench-runner) for your detector.
2. Create an executable Jar file with the MUBench Runner as its entry point.
3. Decide on a detector Id, e.g., `YourDetector`.
4. Integrate the detector into the benchmark:
   - To test `YourDetector`, you may use [MUBench's debugging support](#debugging).
   - To run experiments on `YourDetector`:
     1. Create a folder for your detector locally on you machine, say, `.../YourDetector`.
     2. Place the executable Jar file at `.../YourDetector/latest/YourDetector.jar`.
     3. Add [detector-version and CLI-version information](#provide-version-information) to `.../YourDetector/releases.yml`.
     4. Mount your detector into MUBench by adding `-v .../YourDetector:/mubench/detectors/YourDetector` to [the Docker command running MUBench](../#setup).
     5. [Run experiments](../mubench.pipeline/#run-experiments) using `YourDetector` as the detector Id.
   - To get `YourDetector` published with MUBench:
     1. Fork and clone this repository.
     2. Place the executable Jar file at `detectors/YourDetector/latest/YourDetector.jar`.
     3. Add [detector-version and CLI-version information](#provide-version-information) to `.../YourDetector/releases.yml`.
     4. Create a Pull Request with these new files.

Feel free to [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann), if you have questions or require assistance.


## Implement a MUBench Runner

To run your detector in MUBench experiments, you need to implement a MUBench Runner that invokes your detector and reports its findings.
We provide infrastructure for implementing runners in the Maven dependency `de.tu-darmstadt.stg:mubench.cli` via our repository

    http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/

Check the [MUBench CLI documentation](http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/cli/) for details on how to implement runners and other utilities available through this dependency.

Once you implemented the runner, you need to bundle it together with your detector into an executable Jar file.
This Jar file must have the runner as its entry point and must be named after your detector, e.g., `YourDetector.jar`.
See the configuration of the `maven-assembly-plugin` in [the `pom.xml` file of our `DemoDetector`](./pom.xml) for an example of how to do this.


## Provide Version Information

Each detector has a `releases.yml` file that provides version information.
The most-simple version of such a file, which suffices to run a detector locally, might look as follows:

```yaml
- cli_version: 0.0.13
  md5: foo
```

* The `cli_version` names the version of the `mubench.cli` dependency used to implement the respective [MUBench Runner](#implement-a-mubench-runner).
* The `md5` might be any string.
  When running experiments, [the MUBench Pipeline](../mubench.pipeline) uses this string only to determine whether the detector changed (by checking whether the `md5` changed) and to invalidate existing results accordingly.
  Only when the detector is integrated into the MUBench detector repository, such that [the MUBench Pipeline](../mubench.pipeline) can download it automatically, the `md5` needs to be changed to the actual hash of the Jar file, for download verification.

It is possible to manage multiple versions of a detector via the `releases.yml` file.
The file might then look as follows:

```yaml
- cli_version: 0.0.10
  md5: 2470067fac02ee118b7d49287246e20a
- cli_version: 0.0.8
  md5: 9e5252816faecf552464f0a6abde714f
  tag: my-tag
```

* The `cli_version` names the version of the `mubench.cli` dependency used to implement the respective [MUBench Runner](#implement-a-mubench-runner).
* The `md5` is the hash of the respective Jar file.
* The `tag` is an identifier for the detector version (case insensitive).
  You may specify this identifier when running experiments, using the `--tag` option.
  If the `--tag` option is not specified, [the MUBench Pipeline](../mubench.pipeline) runs the top-most detector version listed in the `releases.yml` file.
  If this detector version has no `tag`, `latest` is used as the default.
  In any case, [the MUBench Pipeline](../mubench.pipeline) expects the respective Jar file at `detectors/<mydetector>/<tag>/<mydetector>.jar`.


## Debugging a Detector

MUBench supports testing and debugging [MUBench Runners](#implement-a-mubench-runner) in its Docker environment using a remote debugger.

### Preparation

1. Mount the directory containing your executable Jar file, e.g., the `target/` directory of your Maven project, into MUBench, by adding `-v /.../target/:/mubench/debug` to [the Docker command running MUBench](../#setup).
2. Forward port `5005` from the shell to your host system, to allow attaching a remote debugger, by adding `-p 5005:5005` to [the Docker command running MUBench](../#setup).

### Debugging

1. Generate `YourDetector.jar`.
2. Run `mubench> debug <CLI> <E> MyDetector <F>`, where
   * `<CLI>` names the version of the `mubench.cli` dependency used to implement your [MUBench Runner](#implement-a-mubench-runner),
   * `<E>` is the [id of the experiment](../mubench.pipeline/#experiments) to run, and
   * `<F>` specifies [a filter](../data/#filtering) (we recommend debugging on individual project versions or misuses, because debug will halt on every(!) single entity).
3. Attach a remote debugger from the IDE of your choice to the local process on port `5005`, once MUBench started the detector.
4. Debug, make changes, and repeat from 1., as necessary.

Example: `debug 0.0.13 ex2 DemoDetector --only aclang.587`
