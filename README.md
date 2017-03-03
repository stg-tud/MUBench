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

### Review Site

#### Server Requirements

* PHP 5.6
* MySQL 5.6
* PHP Extensions:
  * php5.6xml
  * php5.6mbstring

#### Setup

1. `$> ./build_backend`
2. Set your database credentials and configure your reviewer credentials (`users`) in [`./php_backend/src/settings.php`](https://github.com/stg-tud/MUBench/blob/master/mubench.reviewsite/src/settings.php).
3. Upload the contents of `./php_backend` to your webserver.
4. Give read/write permissions on the upload and logs directory.
5. Import [`./php_backend/init_db.sql`](https://github.com/stg-tud/MUBench/blob/master/mubench.reviewsite/init_db.sql) into your database.
6. Use `./mubench publish X -s http://<your-sites.url>/index.php/` to publish to your review site. Check `./mubench publish -h` for further details.


## Run MUBench

MUBench is controlled via the command line. Run `./mubench -h` (`./mubench.bar -h`) for details about the available commands and options.

### Run Experiments

The easiest way to run experiments is to execute

    ./mubench publish findings <D> <E> -s <R> -u <RU> -p <RP>

Where `<D>` is the id of the detector to benchmark, `<E>` is the id of the experiment to run, `<R>` is the URL of your review site, `<RU>` is the user name to access your review site as, and `<RP>` is the respective password.

MUBench will run the detector on the misuses specified in the `data` subfolder. The first time a misuse is used in benchmarking, the repository containing that misuse is cloned (this may take a while). Subsequently, the existing clone is used, such that benchmarking runs offline. Before the first detector is run on a project, MUBench compiles the project (this may take a while). Subsequently, the compiled classes are reused. Then the detector is invoked, and finally the results are published to the review site.

You may run individual benchmark steps. See `./mubench -h` for details.

### Review Findings

We are rebuilding the review site. Please come back in a bit.

### <a name="own-detector" /> Benchmark Your Own Detector

For MUBench to run your detector and interpret its results, your detector's executable needs to comply with MUBench's command-line interface. The easiest way to achieve this is for your entry-point class to extend `MuBenchRunner`, which comes with the Maven dependency [`de.tu-darmstadt.stg:mubench.cli`](https://github.com/stg-tud/MUBench/tree/master/mubench.cli) via our repository at `http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/`.

A typical MUBench Runner looks like this:

    public class XYRunner extends MuBenchRunner {
      public static void main(String[] args) {
        new XYRunner().run(args);
      }
      
      void detectOnly(CodePath patternPath, CodePath targetPath, DetectorOutput output) throws Exception {
        ...
      }
      
      void mineAndDetect(CodePath trainingAndTargetPath, DetectorOutput output) throws Exception {
        ...
      }
    }

Currently, Runners should support two run modes:

1. "Detect Only"-mode, where the detector is provided with hand-crafted patterns (a one-method class implementing the correct usage) and some target code to find violations of these patterns in. All input is provided as Java source code and corresponding Bytecode.
2. "Mine and Detect"-mode, where the detector should mine its own patterns in the provided code base and find violations in that same code base. Again, input is provided as source code and corresponding Bytecode.

The `DetectorOutput` is essentially a collection where you add your detector's findings. MUBench expects you to add the findings ordered by the detector's confidence, descending.

To register your own detector to MUBench, the following steps are necessary:

1. Create a new subfolder `my-detector` in the [detectors](https://github.com/stg-tud/MUBench/tree/master/detectors) folder. `my-detector` will be the Id used to refer to your detector when running experiments.
2. Add the executable JAR with your detector as `my-detector/my-detector.jar`.
3. Run MUBench as usual.

### Run on Your Project

MUBench is designed to run detectors on the benchmark projects that come with the it. Nevertheless, you can also use MUBench to run a detector on your own code, with a few simple steps:

1. Create the folder `data/<project>/versions/<version>/compile`, with arbitrary names for `project` and `version`.
2. Copy/move your project code into that `compile` folder.
3. Create a file `data/<project>/project.yml` with the content:
    ```
    name: <Your Project's Display Name>
    repository:
      type: synthetic
    ```
    This instructs MUBench to use the `compile` folder as the project's "repository". Note that MUBench will copy the entire folder in its compile phase.
    
4. Create a file `data/<project>/versions/<version>/version.yml` with the content:
    ```
    build:
      src: "<src-root>"
      commands:
        - echo "fake build"
      classes: "<classes-root>"
    misuses: []
    revision: 0
    ```
    
    The values for `src-root`/`classes-root` are the relative paths to the source/classes folders within the `compile` folder. If you pre-build your project and, thus, have the classes already available, you have to use the fake-build command above to satisfy MUBench. If you need to execute any commands in order to build the project, you may list these below the `commands` key. Our Docker container comes with a couple of build tools, such as Maven, Gradle, and Ant, but may not satisfy all your build requirements. If you only want to run detectors that work on source code, such as MuDetect, you can stay with the fake build, too.
5. Run a detector, e.g., MuDetect, with `./mubench detect MuDetect 2 --only <project>.<version>`.
6. To upload the results to a review site, run `./mubench publish findings MuDetect 2 --only <project>.<version> -s http://<your-sites.url>/index.php/ -u <username> -p <password>` (this will also run detection, if necessary).

## Contribute to MUBench

We want MUBench to grow, so please be welcome to contribute to the dataset and add your detectors to the benchmark.

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
