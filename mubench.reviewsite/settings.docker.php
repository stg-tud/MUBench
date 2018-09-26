<?php
return [
    'settings' => [
        // Database Connection
        'db' => [
            'driver' => 'sqlite',
            'host' => 'localhost',
            'database' => __DIR__ . '/../findings/reviews.sqlite',
            'username' => 'admin',
            'password' => 'admin',
            'charset'   => 'utf8',
            'collation' => 'utf8_unicode_ci',
            'prefix'    => '', // table-name prefix
        ],

        // Relative path to the review site, e.g., if your site is reachable at
        // http://domain.tld/p/ this would be "/p/". Always add a trailing /.
        'site_base_url' => '/',
        
        // Relative path to the directory that files should be stored in upon
        // reception from the MUBench Pipeline. Needs to be writable.
        'upload' => "./upload",
        
        // The default number of findings to display in Experiment P (Precision).
        'default_ex2_review_size' => '20',
    
        'number_of_required_reviews' => 2,

        // Configuration to put the site in blind-review mode. When enabled,
        // reviewer names are replaced by 'reviewer-1', 'reviewer-2', etc. in
        // both the website itself and the URLs.
        // Detector names are replaced according to the mapping specified
        // below.
        'blind_mode' => [
            'enabled' => false,
            'detector_blind_names' => []
        ],

        // Slim 3
        'displayErrorDetails' => true, // set to false in production
        'addContentLengthHeader' => false, // Allow the web server to send the content-length header

        // Logging
        'logger' => [
            'name' => 'mubench',
            'path' => __DIR__ . '/logs/app.log',
            'level' => \Monolog\Logger::DEBUG,
        ]
    ],
    
    // Reviewer login credentials
    'users' => [
        "reviewer1" => "standalone",
        "reviewer2" => "standalone"
    ]
];
