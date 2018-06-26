<?php

namespace MuBench\ReviewSite\Tests;

use MuBench\ReviewSite\Controllers\ReviewsController;

class ReviewsControllerHelper
{

    /** @var ReviewsController */
    public $reviewController;

    public function __construct($container)
    {
        $this->reviewController = new ReviewsController($container);
    }

    function createReview($misuse, $reviewer, $hit, $violations = [], $tags = [])
    {
        $this->reviewController->updateOrCreateReview($misuse->id, $reviewer->id, '-comment-', [['hit' => $hit, 'violations' => $violations]], $tags);
    }

}