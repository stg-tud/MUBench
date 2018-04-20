package de.tu_darmstadt.stg.mubench.cli;

import de.tu_darmstadt.stg.yaml.YamlEntity;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Interfaces between the MUBench Pipeline and detector implementations. For a usage example
 * see {@link de.tu_darmstadt.stg.mubench.demo.DemoRunner}.
 */
@SuppressWarnings("WeakerAccess")
public final class MuBenchRunner {
    private DetectionStrategy detectOnlyStrategy;
    private DetectionStrategy mineAndDetectStrategy;

    /**
     * @param detectOnlyStrategy Run detection in detect-only mode. Should use {@link DetectorArgs#getTrainingSrcPaths()}
     *                           or {@link DetectorArgs#getTrainingClassPath()} to learn correct usages and identify
     *                           respective violations in {@link DetectorArgs#getTargetSrcPaths()} or
     *                           {@link DetectorArgs#getTargetClassPath()}, respectively.
     * @return this runner, for fluent calls
     */
    public MuBenchRunner withDetectOnlyStrategy(DetectionStrategy detectOnlyStrategy) {
        this.detectOnlyStrategy = detectOnlyStrategy;
        return this;
    }

    /**
     * @param mineAndDetectStrategy Run detection in mine-and-detect mode. Should identify misuses in
     *                              {@link DetectorArgs#getTargetSrcPaths()} or
     *                              {@link DetectorArgs#getTargetClassPath()}.
     *                              May use {@link DetectorArgs#getTargetSrcPaths()} and
     *                              {@link DetectorArgs#getTargetClassPath()} for pattern mining.
     * @return this runner, for fluent calls
     */
    public MuBenchRunner withMineAndDetectStrategy(DetectionStrategy mineAndDetectStrategy) {
        this.mineAndDetectStrategy = mineAndDetectStrategy;
        return this;
    }

    /**
     * Invoke the runner.
     *
     * @param args the command-line arguments passed from the MUBench Pipeline.
     * @throws Exception on errors
     */
    @SuppressWarnings("unused")
    public void run(String[] args) throws Exception {
        DetectorArgs detectorArgs = DetectorArgs.parse(args);
        DetectorOutput output = detect(detectorArgs);
        report(output.getFindings(), detectorArgs.getFindingsFile());
        report(output.getRunInfo(), detectorArgs.getRunInfoFile());
    }

    private DetectorOutput detect(DetectorArgs args) throws Exception {
        switch (args.getDetectorMode()) {
            case DETECT_ONLY:
                return detect(detectOnlyStrategy, args);
            case MINE_AND_DETECT:
                return detect(mineAndDetectStrategy, args);
            default:
                throw new IllegalArgumentException("Unsupported run mode: " + args.getDetectorMode());
        }
    }

    private DetectorOutput detect(DetectionStrategy strategy, DetectorArgs args) throws Exception {
        if (strategy == null) {
            throw new UnsupportedOperationException("detector mode not supported");
        }
        DetectorOutput.Builder builder = new DetectorOutput.Builder();
        return strategy.detectViolations(args, builder);
    }

    private void report(YamlEntity entity, Path findingsFile) throws IOException {
        try (OutputStream os = Files.newOutputStream(findingsFile)) {
            entity.write(os);
        }
    }
}
