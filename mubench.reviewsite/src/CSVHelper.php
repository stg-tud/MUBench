<?php
namespace MuBench\ReviewSite;


class CSVHelper
{

    public function exportStatistics($experiment, $stats)
    {
        $rows[] = ["sep=,"];
        if (strcmp($experiment, "ex1") === 0) {
            $rows[] =
                ["detector", "project", "synthetics", "misuses", "potential_hits", "open_reviews", "need_clarification",
                    "yes_agreements", "no_agreements", "total_agreements", "yes_no_agreements", "no_yes_agreements",
                    "total_disagreements", "kappa_p0", "kappa_pe", "kappa_score", "hits", "recall"];
        } elseif (strcmp($experiment, "ex2") === 0) {
            $rows[] = ["detector", "project", "potential_hits", "open_reviews", "need_clarification", "yes_agreements",
                "no_agreements", "total_agreements", "yes_no_agreements", "no_yes_agreements", "total_disagreements",
                "kappa_p0", "kappa_pe", "kappa_score", "hits", "precision"];
        } else {
            $rows[] = ["detector", "project", "misuses", "potential_hits", "open_reviews", "need_clarification",
                "yes_agreements", "no_agreements", "total_agreements", "yes_no_agreements", "no_yes_agreements",
                "total_disagreements", "kappa_p0", "kappa_pe", "kappa_score", "hits", "recall"];
        }
        foreach ($stats as $key => $stat) {
            $columns = [];
            $columns[] = $stat->getDisplayName();
            $columns[] = $stat->number_of_projects;
            if (strcmp($experiment, "ex1") === 0) {
                $columns[] = $stat->number_of_synthetics;
            }
            if (strcmp($experiment, "ex1") === 0 || strcmp($experiment, "ex3") === 0) {
                $columns[] = $stat->number_of_misuses;
            }
            $kappa_p0 = $stat->getKappaP0();
            $kappe_pe = $stat->getKappaPe();
            $kappa_score = $stat->getKappaScore();
            if (strcmp($experiment, "ex2") === 0) {
                $recall = $stat->getPrecision();
            } else {
                $recall = $stat->getRecall();
            }

            $columns[] = $stat->misuses_to_review;
            $columns[] = $stat->open_reviews;
            $columns[] = $stat->number_of_needs_clarification;
            $columns[] = $stat->yes_agreements;
            $columns[] = $stat->no_agreements;
            $columns[] = $stat->getNumberOfAgreements();
            $columns[] = $stat->yes_no_disagreements;
            $columns[] = $stat->no_yes_disagreements;
            $columns[] = $stat->getNumberOfDisagreements();
            $columns[] = $kappa_p0;
            $columns[] = $kappe_pe;
            $columns[] = $kappa_score;
            $columns[] = $stat->number_of_hits;
            $columns[] = $recall;
            $rows[] = $columns;
        }
        return $this->createCSV($rows);
    }

    private function createCSV($lines)
    {
        $imploded_lines = [];
        foreach ($lines as $line) {
            $imploded_lines[] = implode(',', $line);
        }
        return implode("\n", $imploded_lines);
    }

    public function exportRunStatistics($runs)
    {
        $rows[] = ["sep=,"];
        $rows[] = ["project", "version", "result", "number_of_findings", "runtime", "misuse", "decision",
            "resolution_decision", "resolution_comment"];
        $max_review_count = 2;
        foreach ($runs as $run) {
            $run_details =
                [$run['project'], $run['version'], $run['result'], $run['number_of_findings'], $run['runtime']];
            foreach ($run['misuses'] as $misuse) {
                $columns = $run_details;

                $reviews = $misuse->getReviews();
                $review_count = count($reviews);

                $columns[] = $misuse->id;
                $columns[] = $misuse->getReviewState();
                if ($misuse->hasResolutionReview()) {
                    $resolution = $misuse->getResolutionReview();
                    $columns[] = $resolution->getDecision();
                    $columns[] = "\"" . $resolution->getComment() . "\"";
                } else {
                    $columns[] = "";
                    $columns[] = "";
                }
                foreach ($reviews as $review) {
                    $columns[] = $review->getReviewerName();
                    $columns[] = $review->getDecision();
                    $columns[] = "\"" . $review->getComment() . "\"";
                }
                if ($review_count > $max_review_count) {
                    $max_review_count = $review_count;
                }
                $rows[] = $columns;
            }
            if (empty($run['misuses'])) {
                $rows[] = $run_details;
            }
        }
        for ($i = 1; $i < $max_review_count; $i++) {
            $rows[1][] = "review{$i}_name";
            $rows[1][] = "review{$i}_decision";
            $rows[1][] = "review{$i}_comment";
        }
        return $this->createCSV($rows);
    }
}