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
	
	@Test
	public void invokesDetectOnly() throws Exception {
		MuBenchRunner runner = spy(MuBenchRunner.class);

		runner.run(new DetectorArgs(tmpFile, tmpFile, DetectorMode.DETECT_ONLY, ":trainingSrc:", ":trainingClass:",
				":targetSrc:", ":targetClass:", "dep.jar"));

		verify(runner).detectOnly(
				eq(new CodePath(":trainingSrc:", ":trainingClass:")),
				eq(new CodePath(":targetSrc:", ":targetClass:")),
				eq(new String[] {"dep.jar"}),
				any(DetectorOutput.class));
	}
	
	@Test
	public void invokesMineAndDetect() throws Exception {
		MuBenchRunner runner = spy(MuBenchRunner.class);

		runner.run(new DetectorArgs(tmpFile, tmpFile, DetectorMode.MINE_AND_DETECT, ":trainingSrc:", ":trainingClass:",
				":targetSrc:", ":targetClass:", "dep.jar"));

		verify(runner).mineAndDetect(
				eq(new CodePath(":targetSrc:", ":targetClass:")),
				eq(new String[] {"dep.jar"}),
				any(DetectorOutput.class));
	}
}
