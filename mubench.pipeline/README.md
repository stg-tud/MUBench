<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Pipeline

The MUBench Pipeline allows running experiments on API-misuse detectors, to measure their precision and recall.
To enable platform-independent execution of experiments, we recommend using the `pipeline` command within the MUBench Interactive Shell.
Check `pipeline -h` for details about the available subcommands and options.


## Computing Resources

Specific requirements depend on the detector you evaluate, but our minimum recommendations are:

* CPUs: &ge;2
* Memory: &ge;8.0 GB

*Hint:* Docker limits the computing resources available to experiment runs.
You can adjust this in the advanced preferences.

*Hint:* You also have to make the memory available to the JVM for the detector run, by passing `--java-options Xmx8G` to the `pipeline` command.


## Experiments

The MUBench Pipeline supports the following experiments to measure the precision and recall of API-misuse detectors:

* **P**recision Experiment (`ex2`)

  Measures the precision of the detectors. It runs the detector on real-world projects and requires reviews of the top-N findings per target project, in order to determine the precision.
  
* **R**ecall **U**pper **B**ound Experiment (`ex1`)

  Measures the recall upper bound of detectors. It provides detector with hand-crafted examples of correct usage corresponding to the [known misuses in the dataset](../data), as a reference for identifying misuses. Requires reviews of all potential hits, i.e., findings in the same method as a [known misuse](../data), in order to determine the recall upper bound.
  
* **R**ecall Experiment (`ex3`)
  
  Measures the recall of detectors. It runs the detector on real-world projects and requires reviews of all potential hits, i.e., findings in the same method as a [known misuse](../data), in order to determine the recall.


## Run Experiments

The base command to run an experiment is

    mubench> pipeline run <E> <D> --datasets <DS>

Where

* `<E>` is the [id of the experiment](#experiments) to run,
* `<D>` is the [id of the detector](../detectors), and
* `<DS>` specifies [the dataset](../data/#filtering) to use for the experiment.

Example: `mubench> pipeline run ex2 DemoDetector --datasets TSE17-ExPrecision`

*Hint:* The `--datasets` filter is optional.
We recommend to always [use a filter](../data/#filtering), since running on the entire benchmark requires much disk space and time.

The first time the pipeline runs a detector on a certain project, the project is cloned from version control and compiled.
These preparation steps may take a while.
Subsequently, MUBench uses the local clone and the previously compiled classes, such that experiments may run offline and need very little preparation time.

*Hint:* You may run the preparation steps individually. See `pipeline -h` for details.

The pipeline will store detector findings after execution and, subsequently, skip running a detector on a project version it ran on before, unless the detector or the project version changed in the meantime.
To force the pipeline to rerun the detector use the `--force-detect` option.

Check `pipeline run -h` for further details.

If you want [publish detector findings to a review site](../mubench.reviewsite/#publish-detector-findings), you may run

    mubench> pipeline publish <E> <D> --datasets <DS> -s <R> -u <RU> -p <RP>

Where

* `<E>`, `<D>`, and `<DS>` are as above.
* `<R>` is the URL of [your review site](../mubench.reviewsite/), and
* `<RU>` and `<RP>` are the username and password to access your review site with.

Example: `pipeline publish ex2 DemoDetector --datasets TSE17-ExPrecision -s http://artifact.page/tse17/ -u sven -p 1234`

Running `pipeline publish` implicitly calls `pipeline run`.

Check `pipeline publish -h` for further details.


## Experiment Data

When running experiments, MUBench persists experiment data on the host machine.
This data is stored in [Docker Volumes](https://docs.docker.com/storage/volumes/), which are mounted into the experiment environment:

* `mubench-checkouts` stores the project checkouts and compiled classes (mount point: `/mubench/checkouts`)
* `mubench-findings` stores the detector-run information and detector findings (mount point: `/mubench/findings`)

You can manually browse this data in a MUBench Interactive Shell at the designated mount points.

*Hint*: If you do not mount a volume to these mount points, any respective data is lost when you exit the MUBench Interactive Shell.


## Default Configuration

You can specify defaults for command-line arguments by creating a `./default.config` in [the YAML format](http://yaml.org/).
Values for all command-line arguments that begin with `--` may be specified in this file using the argument's full name as the key.
To set command-line flags by default, use `True` as their value.
For an example on how to do this, see our [example default.config](../default.example.config).

Argument values specified on the command line always take precedence over respective default values.

To use your `default.config` for the MUBench Pipeline, add `-v /.../your.default.config:/mubench/mubench.pipeline/default.config` to [the Docker command running MUBench](../#setup).
