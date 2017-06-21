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
7. Go to `http://<your-site.url>/`.

## Use

`$> ./mubench publish X -s http://<your-sites.url>/index.php/` publishes experiment results to your review site. Check [Run Benchmark Experiments](../mubench.pipeline/) and `./mubench publish -h` for further details.
