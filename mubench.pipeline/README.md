<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Pipeline

MUBench is controlled via the command line. Run `./mubench -h` (`./mubench.bar -h`) for details about the available commands and options.

#### Computing Resources

Docker limits the computing resources available to a docker run. You can adjust this in the advanced preferences. Our recommendations are

* CPUs: &ge;2
* Memory: &ge;8.0 GB

Remember that you may also have to provide more memory to the JVM for the detector run, for example, by passing `--java-options Xmx8G` to the pipeline invocation.


### Run Experiments

The easiest way to run experiments is to execute

    ./mubench publish findings <D> <E> -s <R> -u <RU> -p <RP>

Where `<D>` is the id of the detector to benchmark, `<E>` is the id of the experiment to run, `<R>` is the URL of your review site, `<RU>` is the user name to access your review site as, and `<RP>` is the respective password.

MUBench will run the detector on the misuses specified in the `data` subfolder. The first time a misuse is used in benchmarking, the repository containing that misuse is cloned (this may take a while). Subsequently, the existing clone is used, such that benchmarking runs offline. Before the first detector is run on a project, MUBench compiles the project (this may take a while). Subsequently, the compiled classes are reused. Then the detector is invoked, and finally the results are published to the review site.

You may run individual benchmark steps. See `./mubench -h` for details.

### Add Misuses

To contribute to the MUBench dataset, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) with details about the misuses. For each misuse, please provide

* A description of the misuse (and its fix).
* A link to the website of the project you found the misuse in.
* A link to the project's publicly-readable version-control system, and a commit id to a version with the misuse or, ideally, to the commit that resolves the misuse.
* The misuse's location (file, method, and misused API).
* Instructions how to compile the project in the respective version.

## License

All software provided in this repository is subject to the [CRAPL license](https://github.com/stg-tud/MUBench/tree/master/CRAPL-LICENSE.txt).

The detectors included in MuBench are subject to the licensing of their respective creators. See the information in [the detectors' folders](https://github.com/stg-tud/MUBench/tree/master/detectors).

The projects referenced in the MuBench dataset are subject to their respective licenses.

The project artwork is subject to the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).


