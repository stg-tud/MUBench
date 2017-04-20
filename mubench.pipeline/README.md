<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Pipeline

MUBench is controlled via the command line. Run `./mubench -h` (`./mubench.bat -h`) for details about the available commands and options.

## Computing Resources

Docker limits the computing resources available to a docker run. You can adjust this in the advanced preferences. Our recommendations are

* CPUs: &ge;2
* Memory: &ge;8.0 GB

Remember that you may also have to provide more memory to the JVM for the detector run, for example, by passing `--java-options Xmx8G` to the pipeline invocation.


## Run Experiments

The easiest way to run experiments is to execute

    ./mubench publish findings <D> <E> -s <R> -u <RU> -p <RP>

Where `<D>` is the id of the detector to benchmark, `<E>` is the id of the experiment to run, `<R>` is the URL of your review site, `<RU>` is the user name to access your review site as, and `<RP>` is the respective password.

MUBench will run the detector on the misuses specified in the `data` subfolder. The first time a misuse is used in benchmarking, the repository containing that misuse is cloned (this may take a while). Subsequently, the existing clone is used, such that benchmarking runs offline. Before the first detector is run on a project, MUBench compiles the project (this may take a while). Subsequently, the compiled classes are reused. Then the detector is invoked, and finally the results are published to the review site.

You may run individual benchmark steps. See `./mubench -h` for details.
