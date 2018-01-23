package de.tu_darmstadt.stg.mubench.cli;

public interface DetectionStrategy {
    DetectorOutput detectViolations(DetectorArgs args, DetectorOutput.Builder output) throws Exception;
}
