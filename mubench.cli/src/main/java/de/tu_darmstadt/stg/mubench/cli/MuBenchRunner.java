package de.tu_darmstadt.stg.mubench.cli;

import de.tu_darmstadt.stg.yaml.YamlEntity;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Implement a concrete runner like this:
 * <pre><code>
 * public class XYRunner {
 *   public static void main(String[] args) {
 *     new MuBenchRunner().
 *       .withDetectOnlyStrategy(DetectorArgs as -> List&lt;Violation&gt;()) // detection using provided patterns
 *       .withMineAndDetectStrategy(DetectorArgs as -> List&lt;Violation&gt;()) // detected using own patterns
 *       .run(args);
 *   }
 * }
 * </code></pre>
 */
@SuppressWarnings("WeakerAccess")
public class MuBenchRunner {
    private DetectionStrategy detectOnlyStrategy;
    private DetectionStrategy mineAndDetectStrategy;

    /**
     * @param detectOnlyStrategy    Run detection in detect-only mode. Should use {@link DetectorArgs#getPatternPath()}
     *                              to extract patterns and identify respective violations in
     *                              {@link DetectorArgs#getTargetPath()}.
     */
    public MuBenchRunner withDetectOnlyStrategy(DetectionStrategy detectOnlyStrategy) {
        this.detectOnlyStrategy = detectOnlyStrategy;
        return this;
    }

    /**
     * @param mineAndDetectStrategy Run detection in mine-and-detect mode. Should identify misuses in
     *                              {@link DetectorArgs#getTargetPath()}. May use {@link DetectorArgs#getTargetPath()}
     *                              for pattern mining.
     */
    public MuBenchRunner withMineAndDetectStrategy(DetectionStrategy mineAndDetectStrategy) {
        this.mineAndDetectStrategy = mineAndDetectStrategy;
        return this;
    }

    @SuppressWarnings("unused")
    public void run(String[] args) throws Exception {
        DetectorArgs detectorArgs = DetectorArgs.parse(args);
        DetectorOutput output = detect(detectorArgs);
        report(output.getFindings(), detectorArgs.getFindingsFile());
        report(output.getRunInfo(), detectorArgs.getRunInfoFile());
    }

    protected DetectorOutput detect(DetectorArgs args) throws Exception {
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
        return strategy.detectViolations(args);
    }

    protected void report(YamlEntity entity, Path findingsFile) throws IOException {
        try (OutputStream os = Files.newOutputStream(findingsFile)) {
            entity.write(os);
        }
    }
}
