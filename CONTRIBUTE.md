# Contribute to the MUBench Platform

While we invested a lot into the MUBench platform, to increase its usability and support different experiment scenarios, there is always one more thing to do.
Therefore, we always welcome contributions to the platform itself, be it in code or documentation.
We recommend the following procedure

1. Choose an [issue](https://github.com/stg-tud/MUBench/issues) or [create a new issue](https://github.com/stg-tud/MUBench/issues/new) to discuss the idea you want to work on.
2. [Fork the project](https://github.com/stg-tud/MUBench/fork).
3. Make you changes and add respective tests.
4. Create a pull request.

The MUBench platform consists of several components.
The subsequent documentation presents the purpose and covers specifics regarding the development of each of these components, as well as the project's [Continuous Integration/Deployment](#continuous-integration-and-deployment).


## The MUBench Pipeline

Is a Python application that manages the benchmarking dataset, checkout of subject project code, compilation of subject projects, execution of detectors, and capturing of detector output.

Its source code resides in the [/mubench.pipeline](mubench.pipeline) directory.

### Release

See [Docker Image](#docker-image).


## MUBench Pipeline Java Utils
  
Is a Java library with some utilities used by the [MUBench Pipeline](#the-mubench-pipeline).

Its source code resides in the [/mubench.utils](mubench.utils) directory.

### Release

To release a new version of the Java utils, follow these steps:

1. Set the version in the [`pom.xml`](mubench.utils/pom.xml) file to the next release version, e.g., `0.0.5`.
2. Run `mvn deploy`.[<sup>A</sup>](#auth)
3. Set the version in the [`pom.xml`](mubench.utils/pom.xml) file to the next development version, e.g., `0.0.6-SNAPSHOT`.
4. Obtain the `md5` hash of the `target/mubench.utils-0.0.5-jar-with-dependencies.jar` file.
5. Update the constants `__UTILS_VERSION` and `__UTILS_JAR_MD5` at the top of [`/mubench.pipeline/utils/java_utils.py`](mubench.pipeline/utils/java_utils.py) accordingly.
4. Commit and publish the change.


## MUBench Pipeline CLI

Is a Java library with the framework and some utilities for [MUBench Runners](mubench.cli/#implement-a-mubench-runner).

Its source code resides in the [/mubench.cli](mubench.cli) directory and its [API documentation on the STG artifact page](http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/cli/).

### Release

To release a new version of the CLI, follow these steps:

1. Set the version in the [`pom.xml`](mubench.cli/pom.xml) file to the next release version, e.g., `0.0.14`.
2. Run `mvn deploy`.[<sup>A</sup>](#auth)
3. Run `mvn site deploy`.[<sup>A</sup>](#auth)
4. Set the version in the [`pom.xml`](mubench.cli/pom.xml) file to the next development version, e.g., `0.0.15-SNAPSHOT`.
5. If the new release changes the way that the [MUBench Pipeline](#the-mubench-pipeline) should communicate with [MUBench Runners](mubench.cli/#implement-a-mubench-runner), create a respective subclass of `RunnerInterface` in `/mubench.pipeline/data/runner_interface.py`.
6. Commit and publish the change.


## MUBench Review Site

Is a PHP application that manages the display of detector findings in MUBench experiments, manual reviews of these findings, as well as computation of statistics on the experiment results.

Its source code resides in the [/mubench.reviewsite](mubench.reviewsite) directory.

### Release

See [Docker Image](#docker-image).


## Docker Image

MUBench comes with a [Docker image](docker/Dockerfile) to enable cross-platform portability of the benchmark.
We use this image also as a medium to deliver the MUBench Pipeline and the MUBench Review Site to users.

### Release

A development version of the docker image is continuously deployed to Dockerhub with every succeeding [CI build](#continuous-integration-and-deployment) of the `master` branch of this repository.

To release a stable version of the docker image, run [`./deploy_release`](deploy_release) in the repository root.
This will publish the version currently checked out to Dockerhub, using the `stable` tag.


## Continuous Integration and Deployment

The MUBench project uses [Shippable](https://app.shippable.com/) for Continuous Integration of the platform components described above.
This involves [a custom Docker image](docker/Dockerfile_ci) to support building and testing all modules in one build, despite the multitude of different programming languages in use.

The CI configuration resides in [shippable.yml](shippable.yml).

After a successful build on the `master` branch, a new version of [the MUBench Docker image](#docker-image) is built and deployed to Dockerhub, using the `latest` tag.

---

<a name="auth"><sup>A</sup></a>Deployment requires authentication credentials for `stg-mubench` in your `~/.m2/settings.xml` to deploy the new library version to `ftp://www.st.informatik.tu-darmstadt.de/mubench/mvn`.
