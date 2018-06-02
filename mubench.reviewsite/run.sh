#!/bin/bash

java -jar /usr/local/bin/selenium-server-standalone-3.12.0.jar &> /dev/null &
php -S localhost:8080 -t /mubench/mubench.reviewsite &> /dev/null &
phpunit --bootstrap vendor/autoload.php tests/
