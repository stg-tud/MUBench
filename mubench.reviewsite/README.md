<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Review Site

Evaluating an API-misuse detector in MUBench requires manual reviews of (a subset of) the detector's findings on the benchmark projects.
To facilitate these reviews, the [MUBench Pipeline](../mubench.pipeline) publishes detector findings to a review (web)site.
See [the review site of our TSE article 'A Systematic Evaluation of Static API-Misuse Detectors'](http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/reviews/tse17/) for an example of such a site.
To use MUBench, you need to either obtain an account for an existing review site or [setup your own](#setup).


## Setup

For testing purposes or private use, you may [host a review site standalone](#standalone) using our Docker image.
For hosting a public review site, we recommend [installing the review-site application on a webserver](#on-a-webserver) of your choice.

### On a Webserver 

#### Webserver Requirements

* PHP 7.x (for a list of the necessary PHP extensions, check our [Dockerfile](../docker/Dockerfile_shell)).
* An SQL database and the respective PHP PDO extension (tested with SQLite and MySQL).

#### Setup Instructions

1. Copy the review-site application from our Docker image:
    1. `$> id=$(docker create svamann/mubench:stable)`
    2. `$> docker cp $id:/mubench/mubench.reviewsite - > reviewsite.tar`
    3. `$> docker rm -v $id`
    3. Unpack the tar file on your machine.
2. Copy [`mubench.reviewsite/settings.default.php`](settings.default.php) to `mubench.reviewsite/settings.php` (override the existing `settings.php`, which contains the configuration for running standalone within a Docker container).
4. Adjust `settings.php` to your environment:
    * Enter your database-connection details below `db`.
    * Enter your `site_base_url`, e.g., `/mubench`
    * List your reviewer credentials below `users`.
5. Upload the application to your webserver, e.g., `http://your.site/mubench/`.
6. Grant the server read/write permissions on the `upload` and `logs` directories.
7. Go to `http://your.site/mubench/`, which will initialize your database on the first visit.
8. Delete the `setup` folder from your webserver.
9. Use your review site:
    * [Publish misuse metadata](#publish-misuse-metadata)
    * [Publish detector findings](#publish-detector-findings)
    * Review detector findings

### Standalone

You may run a MUBench review site using our Docker container.
Note, however, that this uses [PHP's built-in webserver](http://php.net/manual/en/features.commandline.webserver.php), which is not a full-featured webserver and discouraged for use on a public network.

1. Run `mubench> reviewsite start`. To access the site from your host system, you need to forward port `80` from the shell to your host system, e.g., by specifying `-p 8080:80` in the docker command that opens the shell.
2. Go to `http://localhost:8080/`, which will initialize your database on the first visit.
3. [Publish misuse metadata](#publish-misuse-metadata), [publish detector findings](#publish-detector-findings), and review detector findings.

Check `reviewsite -h` for further details.


## Publish Misuse Metadata

To correctly display potential hits for known misuses from the dataset, the review site needs the misuse metadata, such as the description, the misuse location, and the misuse code.
To upload the metadata to your review site, simply execute:

    mubench> pipeline publish metadata -s http://your.site/mubench/ -u <user> -p <password>

Check `pipeline publish metadata -h` for further details.

*Hint:* You may want to use the filter options (`--datasets`, `--only`, `--skip`) to upload metadata selectively.


## Publish Detector Findings

After running experiments with a detector, you may publish the detector's findings to your review site using:

    mubench> publish <experiment> <detector> -s http://your.site/mubench/ -u <user> -p <password>

This will [run the respective experiment](../mubench.pipeline/), if you did not do so before.

Check `pipeline publish -h` for further details.

*Hint:* You may want to use the filter options (`--datasets`, `--only`, `--skip`, `--limit`) to upload findings selectively.


## Known Issues

### Cannot login as a reviewer

*Scenario:* You configured a user in your `settings.php`, but when you click `Login` and enter the credentials, the login prompt just reappears, as if you had typed in wrong credentials.
This happens if your server is not forwarding the Basic Auth headers to the review-site application.

*Solution:* Try adding following line to the `.htaccess` file in the base directory of your MUBench review site:

```
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization},L]
```

If this doesn't work, you may try to replace the entire contents of the `.htaccess` file with the following configuration that has been found to work on some servers (make sure to adjust the `RewriteBase` according to your setting):

```
RewriteEngine On
RewriteCond %{HTTP:Authorization} ^(.*)
RewriteRule .* - [e=HTTP_AUTHORIZATION:%1]
RewriteBase /mubench/
RewriteRule ^index\.php$ - [E=X-HTTP_AUTHORIZATION:%{HTTP:Authorization},QSA,L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . index.php [E=X-HTTP_AUTHORIZATION:%{HTTP:Authorization},QSA,L]
```
