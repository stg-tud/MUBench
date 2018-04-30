<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Pipeline

MUBench comes with a Docker image to allow platform independent execution of experiments.
The MUBench Pipeline offers a command-line interface (via `./mubench` on Linux/OSX and via `./mubench.bat` on Windows).
Check `./mubench -h` for details about the available commands and options.


## Computing Resources

Docker limits the computing resources available to experiment runs.
You can adjust this in the advanced preferences.
Specific requirements depend on the detector you evaluate, but our minimum recommendations are:

* CPUs: &ge;2
* Memory: &ge;8.0 GB

*Hint:* You also have to make the memory available to the JVM for the detector run, by passing `--java-options Xmx8G` to the command-line interface.


## Setup

### Linux/OSX

1. Install [Docker](https://www.docker.com/products/overview#/install_the_platform).
2. `$> cd /mubench/install/path/`
3. `$> docker run --rm -v $PWD:/mubench svamann/mubench git clone https://github.com/stg-tud/MUBench.git .`
4. `$> ./mubench check setup`

### Windows

1. Install [Docker](https://www.docker.com/products/overview#/install_the_platform).
2. `$> cd X:\mubench\install\path\`
3. Depending on your system and Docker version you may have to [enable directory mounts for drive X](https://rominirani.com/docker-on-windows-mounting-host-directories-d96f3f056a2c).
4. `$> docker run --rm -v "%cd:\=/%":/mubench svamann/mubench git clone https://github.com/stg-tud/MUBench.git .`
5. `$> ./mubench.bat check setup`


## Run Experiments

The base command to run an experiment is

    $> ./mubench run <E> <D> --datasets <DS>

Where

* `<E>` is the [id of the experiment](#experiments) to run
* `<D>` is the [id of the detector](../detectors), and
* `<DS>` specifies [the dataset](../data/#filtering) to use for the experiment.

The first time MUBench runs a detector on a certain project, that project is cloned from version control and compiled.
These preparation steps may take a while.
Subsequently, MUBench uses the local clone and the previously compiled classes, such that experiments may run offline and need close to no preparation time.

Example: `$> ./mubench run ex2 DemoDetector --datasets TSE17-ExPrecision`

Check `./mubench run -h` for further details.

If you want to run and experiment and immediately [publish detector findings to a review site](../mubench.reviewsite/#publish-detector-findings), you may use

    $> ./mubench publish <E> <D> --datasets <DS> -s <R> -u <RU> -p <RP>

Where

* `<E>`, `<D>`, and `<DS>` are as above.
* `<R>` is the URL of [your review site](../mubench.reviewsite/),
* `<RU>` is the user name to access your review site as, and
* `<RP>` is the respective password.

Example: `./mubench run ex2 DemoDetector --datasets TSE17-ExPrecision -s http://artifact.page/tse17/ -u sven -p 1234`

Check `./mubench publish -h` for further details.

*Hint:* The `--datasets` filter is optional.
We recommend to always [use a filter](../data/#filtering), since running on the entire benchmark requires much disk space and time.

*Hint:* You may run the preparation steps individually. See `./mubench -h` for details.


### Experiments

Available experiments are:

* `ex2` (P) - Measures the precision of the detectors. It runs the detector on real-world projects and requires reviews of the top-N findings per target project, in order to determine the precision.
* `ex1` (RUB) - Measures the recall upper bound of detectors. It provides detector with hand-crafted examples of correct usage corresponding to the [known misuses in the dataset](../data), as a reference for identifying misuses. Requires reviews of all potential hits, i.e., findings in the same method as a [known misuse](../data), in order to determine the recall upper bound.
* `ex3` (R) - Measures the recall of detectors. It runs the detector on real-world projects and requires reviews of all potential hits, i.e., findings in the same method as a [known misuse](../data), in order to determine the recall.


### Default Configuration

You can specify defaults for command-line arguments by creating a `./default.config` in [the YAML format](http://yaml.org/).
Values for all command-line arguments that begin with `--` may be specified in this file using the argument's full name as the key.
To set command-line flags by default, use `True` as their value.
For an example configuration, see [the default.example.config](../default.example.config).
Argument values specified on the command line always take precedence over respective default values.


## Experiment Data

When running experiments, MUBench persists experiment data on the host machine.
This data is stored in [Docker Volumes](https://docs.docker.com/storage/volumes/), which are mounted into the container running an experiment.
Currently, MUBench uses the following volumes:

* `mubench-checkouts` stores the project checkouts and compiled classes (mount point: `/mubench/checkouts`)
* `mubench-findings` stores the detector-run information and detector findings (mount point: `/mubench/findings`)

To manually view the data on the volumes, you can open a Linux shell to a container mounting them with

    $> ./mubench browse
