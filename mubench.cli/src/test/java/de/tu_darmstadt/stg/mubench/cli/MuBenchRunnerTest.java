package de.tu_darmstadt.stg.mubench.cli;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.io.IOException;
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
                .withDetectOnlyStrategy(detectorArgs ->
                        DetectorOutput.create().withFindings(
                                Collections.singletonList(new DetectorFinding(":file:", ":method:"))));

        runner.run(args);

        assertThat(DetectorArgs.parse(args).getFindingsFile(), containsLines("file: ':file:'", "method: ':method:'"));
    }

    @Test
    public void invokesMineAndDetectOnlyStrategy() throws Exception {
        String[] args = createArgs(DetectorMode.MINE_AND_DETECT);
        MuBenchRunner runner = new MuBenchRunner()
                .withMineAndDetectStrategy(detectorArgs ->
                        DetectorOutput.create().withFindings(
                                Collections.singletonList(new DetectorFinding(":file:", ":method:"))));

        runner.run(args);

        assertThat(DetectorArgs.parse(args).getFindingsFile(), containsLines("file: ':file:'", "method: ':method:'"));
    }

    @Test
    public void reportsRunInfo() throws Exception {
        String[] args = createArgs(DetectorMode.DETECT_ONLY);
        MuBenchRunner runner = new MuBenchRunner()
                .withDetectOnlyStrategy(detectorArgs ->
                        DetectorOutput.create().withRunInfo(":key:", ":value:").withFindings(Collections.emptyList()));

        runner.run(args);

        assertThat(DetectorArgs.parse(args).getRunInfoFile(), containsLines("':key:': ':value:'"));
    }

}
