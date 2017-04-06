package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import java.io.FileNotFoundException;

import org.junit.Test;

public class ParseDetectorArgsTest {

	@Test
	public void parseFindingsFile() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs.parse(new String[] { DetectorArgs.keyFindingsFile, "findings.yml" });
		assertEquals("findings.yml", actual.getFindingsFile());
	}
	
	@Test
	public void parseRunFile() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs.parse(new String[] { DetectorArgs.keyRunFile, "run.yml" });
		assertEquals("run.yml", actual.getRunFile());
	}

	@Test
	public void parseDetectorMode() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs.parse(new String[] { DetectorArgs.keyDetectorMode, "0" });
		assertEquals(DetectorMode.MINE_AND_DETECT, actual.getDetectorMode());
	}

	@Test
	public void parseTrainingPaths() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs.parse(
				new String[] { DetectorArgs.keyTrainingSrcPath, "psrc", DetectorArgs.keyTrainingClassPath, "pclasspath" });
		assertEquals("psrc", actual.getPatternSrcPath());
		assertEquals("pclasspath", actual.getPatternClassPath());
	}

	@Test
	public void parseTargetPaths() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs
				.parse(new String[] { DetectorArgs.keyTargetSrcPath, "msrc", DetectorArgs.keyTargetClassPath, "mclasspath" });
		assertEquals("msrc", actual.getTargetSrcPath());
		assertEquals("mclasspath", actual.getTargetClassPath());
	}

	@Test
	public void parseDependenciesClassPath() throws Exception {
		DetectorArgs actual = DetectorArgs.parse(new String[]{DetectorArgs.keyDependenciesClassPath, "foo:bar"});
		assertArrayEquals(new String[] {"foo", "bar"}, actual.getDependencyClassPath());
	}

	@Test(expected = IllegalArgumentException.class)
	public void throwsOnIllegalArgument() {
        DetectorArgs.parse(new String[] { "illegal arg", "value" });
	}
}
