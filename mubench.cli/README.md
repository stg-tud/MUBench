<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Detector Interface

If you want to integrate your detector into MUBench, please follow these steps:

1. [Implement a MUBench Runner](#implement-a-mubench-runner) for your detector.
2. Create an executable JAR with the MUBench Runner as its entry point.
  1. To permanently integrate your detector:
    1. Fork and clone this repository.
    1. Place the executable JAR at `detectors/<mydetector>/latest/<mydetector>.jar`.
    2. Add [detector version and CLI version information](#provide-version-information) to `detectors/<mydetector>/releases.yml`.
    3. Mount your detector into MUBench, by adding `-v /.../detectors/<mydetector>:/mubench/detectors/<mydetector>` to the Docker command running MUBench.
    4. (Optional) Create a Pull Request with these new files, to get them published with the benchmark.
  2. To test your runner, you may use [MUBench's debugging support](#debugging).

Feel free to [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann), if you have questions or require assistance.


## Implement a MUBench Runner

To run your detector in MUBench experiments, you need to configure a MUBench Runner that invokes your detector and reports its findings to [the MUBench Pipeline](../mubench.pipeline).
We provide infrastructure for implementing runners in the Maven dependency `de.tu-darmstadt.stg:mubench.cli` via our repository

    http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/

Check the [MUBench CLI documentation](http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/cli/) for details on how to implement runners and other utilities available through this dependency.

Once you configured the runner, you need to bundle it together with your detector into an executable Jar.
This Jar must have the runner as its entry point.
See the configuration of the `maven-assembly-plugin` in [the `pom.xml` file](./pom.xml) for an example of how we do this for our `DemoDetector`.


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

When debugging a [MUBench Runner](#implement-a-mubench-runner) it can be cumbersome to always copy the changed Jar file into the Docker environment and update the `release.yml` file.
Therefore, you may debug your detector as follows:

### Preparation

1. Mount the directory where your build process writes you executable Jar file to, e.g., the `target/` directory of your Maven project, into MUBench, by adding `-v /.../target/:/mubench/debug` to the Docker command running MUBench.
2. Forward port `5005` from the shell to your host system, to allow attaching a remote debugger, by adding `-p 5005:5005` to the Docker command running MUBench.
3. Start a MUBench Interactive Shell using the modified command.

### Debugging

1. Generate your executable Jar file.
2. Run

   `mubench> debug <CLI> <E> <D> <F>`
   
   Where

  * `<CLI>` names the version of the `mubench.cli` dependency used to implement the respective [MUBench Runner](#implement-a-mubench-runner),
  * `<E>` is the [id of the experiment](#experiments) to run,
  * `<D>` is the id of your detector, i.e., the base name of your executable Jar file, and
  * `<F>` specifies [a filter](../data/#filtering) for a single project version (because debug will halt on every(!) project version).
3. Attach a remote debugger from the IDE of your choice to the local process, once MUBench started the detector.
4. Debug, make changes, and repeat from 1., as necessary.

Example: `debug 0.0.13 ex2 DemoDetector --only aclang.587`
