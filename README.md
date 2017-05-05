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

* ['*MUBench: A Benchmark of API-Misuse Detectors*'](http://sven-amann.de/publications/2016-05-MSR-MUBench-dataset.html)

## Install

### Linux/OSX

1. Install [Docker](https://www.docker.com/products/overview#/install_the_platform).
2. `$> cd /mubench/install/path/`
3. `$> docker run --rm -v $PWD:/mubench svamann/mubench git clone https://github.com/stg-tud/MUBench.git .`
4. `$> ./mubench check`

### Windows

1. Install [Docker](https://www.docker.com/products/overview#/install_the_platform).
2. `$> cd X:\mubench\install\path\`
3. Allow Docker to mount from your X-drive:
  1. Right click the Docker icon in the system tray and choose "Settings."
  2. Open the "Shared Drives" tab.
  3. Ensure that the X-drive is selected and apply.
4. `$> docker run --rm -v "%cd:\=/%":/mubench svamann/mubench git clone https://github.com/stg-tud/MUBench.git .`
5. `$> ./mubench.bat check`

## Use

To use the MUBench pipeline, you need to [Setup a Review Site](mubench.reviewsite/) for MUBench to publish detector results to. Afterwards, you can [Run Benchmark Experiments](mubench.pipeline/).

## Contribute

We want MUBench to grow, so please be welcome to [Add Your Own Project or Misuse to the Dataset](data/) or [Add Your Own Detector](mubench.cli/) to the benchmark.

## License

All software provided in this repository is subject to the [CRAPL license](CRAPL-LICENSE.txt).

The detectors included in MuBench are subject to the licensing of their respective creators. See the information in [the detectors' folders](detectors).

The projects referenced in the MuBench dataset are subject to their respective licenses.

The project artwork is subject to the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
