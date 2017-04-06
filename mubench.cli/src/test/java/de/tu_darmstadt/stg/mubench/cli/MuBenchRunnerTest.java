package de.tu_darmstadt.stg.mubench.cli;

import static org.mockito.Matchers.any;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import java.io.IOException;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

public class MuBenchRunnerTest {
	@Rule
	public TemporaryFolder folder = new TemporaryFolder();
    private String tmpFile;

    @Before
	public void setup() throws IOException {
        tmpFile = folder.newFile().getAbsolutePath();
    }

    private DetectorArgs createArgs(DetectorMode mode) {
        return new DetectorArgs(tmpFile, tmpFile, mode, ":trainingSrc:", ":trainingClass:",
                ":targetSrc:", ":targetClass:", "dep.jar");
    }

	@Test
	public void invokesDetectOnly() throws Exception {
		MuBenchRunner runner = spy(MuBenchRunner.class);
        DetectorArgs args = createArgs(DetectorMode.DETECT_ONLY);

        runner.run(args);

		verify(runner).detectOnly(eq(args), any(DetectorOutput.class));
	}

	@Test
	public void invokesMineAndDetect() throws Exception {
		MuBenchRunner runner = spy(MuBenchRunner.class);
        DetectorArgs args = createArgs(DetectorMode.MINE_AND_DETECT);

		runner.run(args);

		verify(runner).mineAndDetect(eq(args), any(DetectorOutput.class));
	}
}
