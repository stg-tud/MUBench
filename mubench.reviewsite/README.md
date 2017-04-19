<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Review Site

We are rebuilding the review site. Please come back in a bit.

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