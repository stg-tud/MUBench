<?php
namespace MuBench\ReviewSite\Model;

class ReviewState
{
    const NOTHING_TO_REVIEW = 0;
    const NEEDS_REVIEW = 1;
    const NEEDS_CLARIFICATION = 2;
    const DISAGREEMENT = 3;
    const AGREEMENT_YES = 4;
    const AGREEMENT_NO = 5;
    const RESOLVED_YES = 6;
    const RESOLVED_NO = 7;
    const UNRESOLVED = 8;
}
