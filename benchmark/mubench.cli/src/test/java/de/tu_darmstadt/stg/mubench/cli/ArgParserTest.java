package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;

import java.io.FileNotFoundException;

import org.junit.Test;

public class ArgParserTest {

	@Test
	public void parseFindingsFile() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(new String[] { ArgParser.keyFindingsFile, "findings.yml" });
		assertEquals("findings.yml", actual.getFindingsFile());
	}

	@Test
	public void parseDetectorMode() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(new String[] { ArgParser.keyDetectorMode, "0" });
		assertEquals(DetectorMode.MINE_AND_DETECT, actual.getDetectorMode());
	}

	@Test
	public void parseTrainingPaths() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(
				new String[] { ArgParser.keyTrainingSrcPath, "psrc", ArgParser.keyTrainingClassPath, "pclasspath" });
		assertEquals("psrc", actual.getTrainingSrcPath());
		assertEquals("pclasspath", actual.getTrainingClassPath());
	}

	@Test
	public void parseTargetPaths() throws FileNotFoundException {
		DetectorArgs actual = ArgParser
				.parse(new String[] { ArgParser.keyTargetSrcPath, "msrc", ArgParser.keyTargetClassPath, "mclasspath" });
		assertEquals("msrc", actual.getTargetSrcPath());
		assertEquals("mclasspath", actual.getTargetClassPath());
	}

	@Test(expected = IllegalArgumentException.class)
	public void throwsOnIllegalArgument() {
		ArgParser.parse(new String[] { "illegal arg", "value" });
	}
}
