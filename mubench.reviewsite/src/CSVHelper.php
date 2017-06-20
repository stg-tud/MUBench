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
            $result = $result .
                "detector,project,synthetics,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        } elseif (strcmp($experiment, "ex2") === 0) {
            $result = $result .
                "detector,project,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        } else {
            $result = $result .
                "detector,project,misuses,potential_hits,open_reviews,need_clarification,yes_agreements,no_agreements,total_agreements,yes_no_agreements,no_yes_agreements,total_disagreements,kappa_p0,kappa_pe,kappa_score,hits,recall";
        }
        foreach ($stats as $key => $stat) {
            $result = $result . "\n";
            $result = $result . $stat->getDisplayName() . ",";
            $result = $result . $stat->number_of_projects . ",";
            if (strcmp($experiment, "ex1") === 0) {
                $result = $result . $stat->number_of_synthetics . ",";
            }
            if (strcmp($experiment, "ex1") === 0 || strcmp($experiment, "ex3") === 0) {
                $result = $result . $stat->number_of_misuses . ",";
            }
            $result = $result . $stat->misuses_to_review . ",";
            $result = $result . $stat->open_reviews . ",";
            $result = $result . $stat->number_of_needs_clarification . ",";
            $result = $result . $stat->yes_agreements . ",";
            $result = $result . $stat->no_agreements . ",";
            $result = $result . $stat->getNumberOfAgreements() . ",";
            $result = $result . $stat->yes_no_disagreements . ",";
            $result = $result . $stat->no_yes_disagreements . ",";
            $result = $result . $stat->getNumberOfDisagreements() . ",";
            $result = $result . round($stat->getKappaP0(), 3) . ",";
            $result = $result . round($stat->getKappaPe(), 3) . ",";
            $result = $result . round($stat->getKappaScore(), 3) . ",";
            $result = $result . $stat->number_of_hits . ",";
            $result = $result . round($stat->getRecall() * 100, 1) . ",";
        }
        return $result;
    }

    public function createCSVFromRuns($runs)
    {
        return "";
    }
}