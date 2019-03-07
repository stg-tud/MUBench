package de.tu_darmstadt.stg.mubench.demo;

import de.tu_darmstadt.stg.mubench.cli.*;

import java.util.List;

/**
 * This demo class implements a {@link MuBenchRunner} with strategies for all detection modes. It demonstrates how
 * runner can report information on the detector run and how they report detector findings to the MUBench Pipeline.
 */
public class DemoRunner {
    public static void main(String[] args) throws Exception {
        new MuBenchRunner()
                // Strategy for running in detect-only mode, where MUBench provides correct usages for training the
                // detector before mining misuses.
                .withDetectOnlyStrategy((DetectorArgs dargs, DetectorOutput.Builder output) -> {
                    output.withRunInfo("detecting with provided correct usages", "true");

                    long startTime = System.currentTimeMillis();

                    List<DemoViolation> violations = new DemoDetector()
                            .detectViolations(dargs.getTrainingSrcPaths(), dargs.getTargetSrcPaths());

                    long endTime = System.currentTimeMillis();

                    return output
                            .withRunInfo("runtime", endTime - startTime)
                            .withFindings(violations, DemoRunner::toDetectorFinding);
                })
                // Strategy for running in mine-and-detect mode, where the detector should train on the target project
                // itself before mining misuses.
                .withMineAndDetectStrategy((DetectorArgs dargs, DetectorOutput.Builder output) -> {
                    output.withRunInfo("detecting with self-mined patterns", "true");

                    long startTime = System.currentTimeMillis();

                    // Note that we use the target path as training path here, because in this mode no explicit training
                    // data is provided.
                    List<DemoViolation> violations = new DemoDetector()
                            .detectViolations(dargs.getTargetSrcPaths(), dargs.getTargetSrcPaths());

                    long endTime = System.currentTimeMillis();

                    return output
                            .withRunInfo("runtime", endTime - startTime)
                            .withFindings(violations, DemoRunner::toDetectorFinding);
                })
                .run(args);
    }

    /**
     * The conversion of detector violations to findings is trivial in this demo case, but it allows for more complex
     * conversion of detector findings for reporting to MUBench, without changing the existing detector implementation.
     *
     * @param violation the detector findings to report to MUBench
     * @return the passed finding converted to the MUBench format
     */
    private static DetectorFinding toDetectorFinding(DemoViolation violation) {
        return new DetectorFinding(violation.getFile(), violation.getMethod());
    }
}
