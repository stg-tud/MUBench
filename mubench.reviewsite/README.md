<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Review Site

The [MUBench Pipeline](../mubench.pipeline) publishes the detectors' results to a review website for you to assess. See [our demo site](http://mubench2.svamann.de/site/) for an example of how this looks like. To use MUBench, you need to either obtain an account for an existing review site or [setup your own](#setup).

## Server Requirements

* PHP 5.6
* MySQL 5.6
* PHP Extensions:
  * php5.6xml
  * php5.6mbstring

## Setup

1. `$> ./mubench configure review-site`
2. Adjust [`mubench.reviewsite/src/settings.php`](src/settings.php) to your environment:
  - Enter your database configuration below `db`.
  - Enter a prefix (possibly empty) for your database tables in `db/prefix`.
  - List your reviewer credentials below `users`.
3. Upload the contents of `mubench.reviewsite/` to your webserver.
4. Grant the server read/write permissions on the `upload` and `logs` directories.
5. Import [`mubench.reviewsite/init_db.sql`](https://github.com/stg-tud/MUBench/blob/master/mubench.reviewsite/init_db.sql) into your database.
6. Add the table-name prefix you entered in the settings to all tables.
7. [Publish the misuse metadata](#publish-misuse-metadata) to your review site.
8. Go to `http://<your-site.url>/`.

## Publish Misuse Metadata

In Experiments 1 and 3, the review site needs the misuse metadata, such as the description, the pattern code, and the misuse code, in order to display the detectors findings correctly. To upload the metadata to your review site, simply execute:

`$> ./mubench publish metadata -s http://<your-site.url>/index.php/ -u <user> -p <password>`

*Hint:* You may use the usual filter options (`--dataset`, `--only`, `--skip`) to upload metadata selectively.

## Use

`$> ./mubench publish X -s http://<your-sites.url>/index.php/` publishes experiment results to your review site. Check [Run Benchmark Experiments](../mubench.pipeline/) and `./mubench publish -h` for further details.

## Known Issues

### Cannot login as a reviewer

*Scenario:* You configured a user in your `settings.php`, but when you click `Login` and enter the credentials, the login prompt just reappears, as if you had typed in wrong credentials.

*Solution:* The problem might be how PHP Basic Auth is configured on your server. Try adding a `.htaccess` file with the following line to the base directory of your MUBench installation:

```
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization},L]
```
