<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Pipeline

MUBench comes as a Docker container that is controlled via the command line. Run `./mubench -h` for details about the available commands and options.

We provide the same command-line interface for Linux/OSX via `./mubench` and for Windows via `./mubench.bat`.

## Computing Resources

Docker limits the computing resources available to a docker run. You can adjust this in the advanced preferences. Our recommendations are:

* CPUs: &ge;2
* Memory: &ge;8.0 GB

Remember that you may also have to provide more memory to the JVM for the detector run, for example, by passing `--java-options Xmx8G` to the pipeline invocation.


## Run Experiments

The easiest way to run experiments is to execute

    ./mubench publish findings <D> <E> -s <R> -u <RU> -p <RP>

Where `<D>` is the [id of the detector](#detectors), `<E>` is the [number of the experiment](#experiments) to run, `<R>` is the URL of [your review site](../mubench.reviewsite/), `<RU>` is the user name to access your review site as, and `<RP>` is the respective password.

### Detectors

Run `./mubench detect -h` for a list of available detector ids.

### Experiments

Available experiments are:

1. Provide detectors with example code of a correct usage, i.e., a usage pattern, to evaluate the recall of their detection strategy with respect to the misuses in the [MUBench Dataset](../data/) in isolation.
2. Run detectors "in the wild", i.e., both their pattern mining and detection, to evaluate their precision in an end-user setting.
3. Run detectors "in the wild", i.e., both their pattern mining and detection, to evaluate their recall with respect to the misuses in the [MUBench Dataset](../data/).

### Execution

MUBench runs the detectors on the projects/misuses specified in the [MUBench Dataset](../data/). The first time a project is used in benchmarking, the repository containing that project is cloned (this may take a while). Subsequently, the existing clone is used, such that benchmarking runs offline. Before the first detector is run on a project, MUBench compiles the project (this may take a while). Subsequently, the compiled classes are reused. Then the detector is invoked, and finally the results are published to [the review site](../mubench.reviewsite/).

### Advanced Use

You may run individual benchmark steps or select subsets of the entire dataset. See `./mubench -h` for details.
