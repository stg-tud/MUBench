<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Review Site

Evaluating an API-misuse detector in MUBench requires manual reviews of (a subset of) the detector's findings on the benchmark projects.
To facilitate these reviews, the [MUBench Pipeline](../mubench.pipeline) publishes detector findings to a review (web)site.
See [the review site of our TSE article 'A Systematic Evaluation of Static API-Misuse Detectors'](http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/reviews/tse17/) for an example of such a site.
To use MUBench, you need to either obtain an account for an existing review site or [setup your own](#setup).


## Server Requirements

* PHP 7 with the following extensions:
  * `ctype`
  * `dom`
  * `json`
  * `mbstring`
  * `openssl`
  * `pdo`
  * `session`
  * `tokenizer`
  * `xml`
  * `xmlwriter`
  * `zlib`
* An SQL database and the respective PHP PDO extension
  * (Tested with SQLite and MySQL)


## Setup

### On a Webserver 

To setup a MUBench review site on a webserver, proceed as follows:

1. [Setup the MUBench Pipeline](../mubench.pipeline/#setup)
2. `$> ./mubench reviewsite init`
3. Copy [`mubench.reviewsite/settings.default.php`](settings.default.php) to `mubench.reviewsite/settings.php`.
4. Adjust `settings.php` to your environment:
    * Enter your database-connection details below `db`.
    * Enter your `site_base_url`.
    * List your reviewer credentials below `users`.
5. Upload the contents of `mubench.reviewsite/` to your webserver.
6. Grant the server read/write permissions on the `upload` and `logs` directories.
7. Go to `http://<your-site.url/`[`setup/setup.php`](https://github.com/stg-tud/MUBench/blob/master/mubench.reviewsite/setup/setup.php) to initialize your database. **This will override existing tables!**
8. Delete the `setup` folder from your webserver.
9. [Publish misuse metadata](#publish-misuse-metadata) to your review site.

### Standalone

To run a MUBench review site locally on your machine, proceed as follows:

1. [Setup the MUBench Pipeline](../mubench.pipeline/#setup)
2. `$> ./mubench reviewsite init`
3. Copy [`mubench.reviewsite/settings.default.php`](settings.default.php) to `mubench.reviewsite/settings.php`.
4. List your reviewer credentials in `settings.php` below `users`.
5. `$> ./mubench reviewsite start`
6. Go to `http://localhost:8080/`[`setup/setup.php`](https://github.com/stg-tud/MUBench/blob/master/mubench.reviewsite/setup/setup.php) to initialize your database.
7. [Publish misuse metadata](#publish-misuse-metadata) to `http://localhost:8080/`.

Check `./mubench reviewsite -h` for further details.

*Hint:* To shutdown the review site, run `./mubench reviewsite stop`.


## Publish Misuse Metadata

To correctly display potential hits for known misuses in the dataset, the review site needs the misuse metadata, such as the description, the misuse location, and the misuse code.
To upload the metadata to your review site, simply execute:

    $> ./mubench publish metadata -s http://<your-site.url>/ -u <user> -p <password>

Check `./mubench publish metadata -h` for further details.

*Hint:* You may want to use the filter options (`--datasets`, `--only`, `--skip`) to upload metadata selectively.


## Publish Detector Findings

After running experiments with a detector, you may publish the detector's findings to your review site using:

    $> ./mubench publish <experiment> <detector> -s http://<your-sites.url>/ -u <user> -p <password>

This will [run the respective experiment](../mubench.pipeline/), if you did not do so before.

Check `./mubench publish -h` for further details.

*Hint:* You may want to use the filter options (`--datasets`, `--only`, `--skip`, `--limit`) to upload findings selectively.


## Known Issues

### Cannot login as a reviewer

*Scenario:* You configured a user in your `settings.php`, but when you click `Login` and enter the credentials, the login prompt just reappears, as if you had typed in wrong credentials.

*Solution:* The problem might be how PHP Basic Auth is configured on your server.
Try adding following line to the `.htaccess` file in the base directory of your MUBench review site:

```
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization},L]
```
