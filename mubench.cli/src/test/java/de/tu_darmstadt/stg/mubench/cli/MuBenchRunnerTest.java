package de.tu_darmstadt.stg.mubench.cli;

import de.tu_darmstadt.stg.yaml.YamlObject;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;

import static de.tu_darmstadt.stg.yaml.IsStringWithLinesMatcher.containsLines;
import static org.junit.Assert.assertThat;

public class MuBenchRunnerTest {
    @Rule
    public TemporaryFolder folder = new TemporaryFolder();

    private String[] createArgs(DetectorMode mode) throws IOException {
        return new String[]{
                DetectorArgs.keyFindingsFile, folder.newFile().getAbsolutePath(),
                DetectorArgs.keyRunFile, folder.newFile().getAbsolutePath(),
                DetectorArgs.keyDetectorMode, mode.getCode(),
        };
    }

    @Test
    public void invokesDetectOnlyStrategy() throws Exception {
        String[] args = createArgs(DetectorMode.DETECT_ONLY);
        MuBenchRunner runner = new MuBenchRunner()
                .withDetectOnlyStrategy(detectorArgs -> findingsOutput(new DetectorFinding(":file:", ":method:")));

        runner.run(args);

        assertThat(DetectorArgs.parse(args).getFindingsFile(), containsLines("file: ':file:'", "method: ':method:'"));
    }

    @Test
    public void invokesMineAndDetectOnlyStrategy() throws Exception {
        MuBenchRunner runner = new MuBenchRunner()
                .withMineAndDetectStrategy(detectorArgs -> findingsOutput(new DetectorFinding(":file:", ":method:")));
        String[] args = createArgs(DetectorMode.MINE_AND_DETECT);

        runner.run(args);

        assertThat(DetectorArgs.parse(args).getFindingsFile(), containsLines("file: ':file:'", "method: ':method:'"));
    }

    @Test
    public void reportsRunInfo() throws Exception {
        String[] args = createArgs(DetectorMode.DETECT_ONLY);
        MuBenchRunner runner = new MuBenchRunner()
                .withDetectOnlyStrategy(detectorArgs -> runInfoOutput(new YamlObject() {{
                    put(":key:", ":value:");
                }}));

        runner.run(args);

        assertThat(DetectorArgs.parse(args).getRunInfoFile(), containsLines("':key:': ':value:'"));
    }

    private static DetectorOutput findingsOutput(DetectorFinding... findings) {
        return new DetectorOutput(Arrays.asList(findings));
    }

    private static DetectorOutput runInfoOutput(YamlObject runInfo) {
        return new DetectorOutput(runInfo, Collections.emptyList());
    }
}
