<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : A Benchmark for API-Misuse Detectors

The MUBench dataset is an [MSR 2016 Data Showcase](http://2016.msrconf.org/#/data) and an benchmarking pipeline for API-misuse detectors. Please feel free to [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann), if you have any questions.

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

## Install MUBench

### Experiment Pipeline

#### Linux/OSX

1. Install [Docker](https://www.docker.com/products/overview#/install_the_platform).
2. `$> cd /mubench/install/path/`
3. `$> docker run --rm -v $PWD:/mubench svamann/mubench git clone https://github.com/stg-tud/MUBench.git .`
4. `$> ./mubench check` (On the first run, this may take some time.)

#### Windows

1. Install [Docker](https://www.docker.com/products/overview#/install_the_platform).
2. `$> cd X:\mubench\install\path\`
3. Allow Docker to mount from your X-drive:
  1. Right click the Docker icon in the system tray and choose "Settings."
  2. Open the "Shared Drives" tab.
  3. Ensure that the X-drive is selected and apply.
4. `$> docker run --rm -v "%cd:\=/%":/mubench svamann/mubench git clone https://github.com/stg-tud/MUBench.git .`
5. `$> ./mubench.bat check` (On the first run, this may take some time).

#### Computing Resources

Docker limits the computing resources available to a docker run. You can adjust this in the advanced preferences. Our recommendations are

* CPUs: &ge;2
* Memory: &ge;8.0 GB

Remember that you may also have to provide more memory to the JVM for the detector run, for example, by passing `--java-options Xmx8G` to the pipeline invocation.

## Run MUBench

MUBench is controlled via the command line. Run `./mubench -h` (`./mubench.bar -h`) for details about the available commands and options.

### Run Experiments

The easiest way to run experiments is to execute

    ./mubench publish findings <D> <E> -s <R> -u <RU> -p <RP>

Where `<D>` is the id of the detector to benchmark, `<E>` is the id of the experiment to run, `<R>` is the URL of your review site, `<RU>` is the user name to access your review site as, and `<RP>` is the respective password.

MUBench will run the detector on the misuses specified in the `data` subfolder. The first time a misuse is used in benchmarking, the repository containing that misuse is cloned (this may take a while). Subsequently, the existing clone is used, such that benchmarking runs offline. Before the first detector is run on a project, MUBench compiles the project (this may take a while). Subsequently, the compiled classes are reused. Then the detector is invoked, and finally the results are published to the review site.

You may run individual benchmark steps. See `./mubench -h` for details.

### Review Findings

We are rebuilding the [review site](https://github.com/stg-tud/MUBench/tree/master/mubench.reviewsite). Please come back in a bit.

## Contribute to MUBench

We want MUBench to grow, so please be welcome to contribute to the dataset and [add your detectors](https://github.com/stg-tud/MUBench/tree/master/mubench.cli) to the benchmark.

### Add Misuses

To contribute to the MUBench dataset, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) with details about the misuses. For each misuse, please provide

* A description of the misuse (and its fix).
* A link to the website of the project you found the misuse in.
* A link to the project's publicly-readable version-control system, and a commit id to a version with the misuse or, ideally, to the commit that resolves the misuse.
* The misuse's location (file, method, and misused API).
* Instructions how to compile the project in the respective version.

### Add Detectors

If you have [a detector set up for running on MUBench](#own-detector), please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) to have it added to the benchmark.

## License

All software provided in this repository is subject to the [CRAPL license](https://github.com/stg-tud/MUBench/tree/master/CRAPL-LICENSE.txt).

The detectors included in MuBench are subject to the licensing of their respective creators. See the information in [the detectors' folders](https://github.com/stg-tud/MUBench/tree/master/detectors).

The projects referenced in the MuBench dataset are subject to their respective licenses.

The project artwork is subject to the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
