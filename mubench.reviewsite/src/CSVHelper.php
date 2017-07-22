<?php
namespace MuBench\ReviewSite;


class CSVHelper
{

    public function exportStatistics($experiment, $stats)
    {
        foreach ($stats as $stat) {
            $row = [];
            $row["detector"] = $stat->getDisplayName();
            $row["project"] = $stat->number_of_projects;

            if (strcmp($experiment, "ex1") === 0) {
                $row["synthetics"] = $stat->number_of_synthetics;
            }
            if (strcmp($experiment, "ex1") === 0 || strcmp($experiment, "ex3") === 0) {
                $row["misuses"] = $stat->number_of_misuses;
            }

            $row["potential_hits"] = $stat->misuses_to_review;
            $row["open_reviews"] = $stat->open_reviews;
            $row["need_clarification"] = $stat->number_of_needs_clarification;
            $row["yes_agreements"] = $stat->yes_agreements;
            $row["no_agreements"] = $stat->no_agreements;
            $row["total_agreements"] = $stat->getNumberOfAgreements();
            $row["yes_no_agreements"] = $stat->yes_no_disagreements;
            $row["no_yes_agreements"] = $stat->no_yes_disagreements;
            $row["total_disagreements"] = $stat->getNumberOfDisagreements();
            $row["kappa_p0"] = $stat->getKappaP0();
            $row["kappa_pe"] = $stat->getKappaPe();
            $row["kappa_score"] = $stat->getKappaScore();
            $row["hits"] = $stat->number_of_hits;

            if (strcmp($experiment, "ex2") === 0) {
                $row["precision"] = $stat->getPrecision();
            } else {
                $row["recall"] = $stat->getRecall();
            }

            $rows[] = $row;
        }
        return $this->createCSV($rows);
    }

    public function exportRunStatistics($runs)
    {
        foreach ($runs as $run) {
            $run_details = [];
            $run_details["project"] = $run["project"];
            $run_details["version"] = $run["version"];
            $run_details["result"] = $run["result"];
            $run_details["number_of_findings"] = $run["number_of_findings"];
            $run_details["runtime"] = $run["runtime"];

            foreach ($run['misuses'] as $misuse) {
                $row = $run_details;

                $row["misuse"] = $misuse->id;
                $row["decision"] = $misuse->getReviewState();
                if ($misuse->hasResolutionReview()) {
                    $resolution = $misuse->getResolutionReview();
                    $row["resolution_decision"] = $resolution->getDecision();
                    $row["resolution_comment"] = $this->escapeText($resolution->getComment());
                } else {
                    $row["resolution_decision"] = "";
                    $row["resolution_comment"] = "";
                }

                $reviews = $misuse->getReviews();
                $review_index = 0;
                foreach ($reviews as $review) {
                    $review_index++;
                    $row["review{$review_index}_name"] = $review->getReviewerName();
                    $row["review{$review_index}_decision"] = $review->getDecision();
                    $row["review{$review_index}_comment"] = $this->escapeText($review->getComment());
                }

                $rows[] = $row;
            }
            if (empty($run['misuses'])) {
                $rows[] = $run_details;
            }
        }
        return $this->createCSV($rows);
    }


    private function createCSV($rows)
    {
        $lines = [];
        $header = [];
        foreach ($rows as $line) {
            $lines[] = implode(',', $line);

            $columns = array_keys($line);
            if(count($columns) > count($header)){
                $header = $columns;
            }
        }
        array_unshift($lines, implode(',', $header));
        array_unshift($lines, "sep=,");
        return implode("\n", $lines);
    }

    private function escapeText($text){
        return "\"" . $text . "\"";
    }

}