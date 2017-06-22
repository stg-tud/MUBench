<?php
namespace MuBench\ReviewSite;


class CSVHelper
{

    function __construct()
    {

    }

    public function createCSVFromStats($experiment, $stats)
    {
        $result = "sep=,\n";
        if (strcmp($experiment, "ex1") === 0) {
            $result .= "detector,project,synthetics,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        } elseif (strcmp($experiment, "ex2") === 0) {
            $result .= "detector,project,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        } else {
            $result .= "detector,project,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        }
        foreach ($stats as $key => $stat) {
            $result .="\n";
            $result .= "{$stat->getDisplayName()},{$stat->number_of_projects},";
            if (strcmp($experiment, "ex1") === 0) {
                $result .= "{$stat->number_of_synthetics},";
            }
            if (strcmp($experiment, "ex1") === 0 || strcmp($experiment, "ex3") === 0) {
                $result .= "{$stat->number_of_misuses},";
            }
            $kappa_p0 = round($stat->getKappaP0(), 3);
            $kappe_pe = round($stat->getKappaPe(), 3);
            $kappa_score = round($stat->getKappaScore(), 3);
            $recall = round($stat->getRecall() * 100, 1);

            $result .= "{$stat->misuses_to_review},";
            $result .= "{$stat->open_reviews},";
            $result .= "{$stat->number_of_needs_clarification},";
            $result .= "{$stat->yes_agreements},";
            $result .= "{$stat->no_agreements},";
            $result .= "{$stat->getNumberOfAgreements()},";
            $result .= "{$stat->yes_no_disagreements},";
            $result .= "{$stat->no_yes_disagreements},";
            $result .= "{$stat->getNumberOfDisagreements()},";
            $result .= "{$kappa_p0},";
            $result .= "{$kappe_pe},";
            $result .= "{$kappa_score},";
            $result .= "{$stat->number_of_hits},";
            $result .= "{$recall},";
        }
        return $result;
    }

    public function createCSVFromRuns($runs)
    {
        $result = "sep=,\n";
        $result .= "project,version,result,number_of_findings,runtime,misuse,decision,resolution_decision,resolution_comment";
        $misuse_entries = [];
        $max_review_count = 2;
        foreach ($runs as $run) {
            $run_details = "{$run['project']},{$run['version']},{$run['result']},{$run['number_of_findings']},{$run['runtime']},";
            foreach ($run['misuses'] as $misuse) {
                $reviews = $misuse->getReviews();
                $review_count = count($reviews);

                $misuse_entry = "{$run_details}{$misuse->id},";
                $misuse_entry .= "{$misuse->getReviewState()},";
                if ($misuse->hasResolutionReview()) {
                    $resolution = $misuse->getResolutionReview();
                    $misuse_entry .= "{$resolution->getDecision()},{$resolution->getComment},";
                } else {
                    $misuse_entry .= ",,";
                }
                foreach ($reviews as $review) {
                    $misuse_entry .= "{$review->getReviewerName()},{$review->getDecision()},{$review->getComment()}";
                }
                if ($review_count > $max_review_count) {
                    $max_review_count = $review_count;
                }
                $misuse_entries[] = $misuse_entry;
            }
            if (empty($run['misuses'])) {
                $misuse_entries[] = $run_details;
            }
        }
        for ($i = 1; $i < $max_review_count; $i++) {
            $result .= ",review{$i}_name";
            $result .= ",review{$i}_decision";
            $result .= ",review{$i}_comment";
        }
        foreach ($misuse_entries as $misuse_entry) {
            $result = $result . "\n" . $misuse_entry;
        }
        return $result;
    }
}