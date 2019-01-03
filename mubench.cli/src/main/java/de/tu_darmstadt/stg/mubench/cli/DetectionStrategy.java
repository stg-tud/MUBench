package de.tu_darmstadt.stg.mubench.cli;

/**
 * A strategy for running a detector with input from the MUBench Pipeline.
 */
public interface DetectionStrategy {
    DetectorOutput detectViolations(DetectorArgs args, DetectorOutput.Builder output) throws Exception;
}
