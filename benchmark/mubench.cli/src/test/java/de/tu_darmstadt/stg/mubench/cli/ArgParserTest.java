package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;

import java.io.FileNotFoundException;

import org.junit.Test;

public class ArgParserTest {
	private static final String testFindingsFile = "findings.yml";
	private static final String testDetectorMode = "0";
	private static final String testProjectSrcPath = "src";
	private static final String testProjectClassPath = "classpath";
	private static final String testMisuseSrcPath = "msrc";
	private static final String testMisuseClassPath = "mclasspath";
	private static final String testPatternsSrcPath = "psrc";
	private static final String testPatternsClassPath = "pclasspath";

	String[] testArgs = new String[] { ArgParser.keyFindingsFile, testFindingsFile, ArgParser.keyProjectSrcPath,
			testProjectSrcPath, ArgParser.keyProjectClassPath, testProjectClassPath, ArgParser.keyMisuseSrcPath,
			testMisuseSrcPath, ArgParser.keyMisuseClassPath, testMisuseClassPath, ArgParser.keyPatternsSrcPath,
			testPatternsSrcPath, ArgParser.keyPatternsClassPath, testPatternsClassPath, ArgParser.keyDetectorMode,
			testDetectorMode };

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoFindingsFile() throws FileNotFoundException {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);

		actual.getFindingsFile();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoProjectSourcePath() throws FileNotFoundException {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);

		actual.getProjectSrcPath();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoProjectClassPath() throws FileNotFoundException {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);

		actual.getProjectClassPath();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoMisuseSourcePath() throws FileNotFoundException {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);

		actual.getMisuseSrcPath();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoMisuseClassPath() throws FileNotFoundException {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);

		actual.getMisuseClassPath();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoPatternSourcePath() throws FileNotFoundException {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);

		actual.getPatternsSrcPath();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoPatternClassPath() throws FileNotFoundException {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);

		actual.getPatternsClassPath();
	}
	
	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoDetectorMode() throws FileNotFoundException {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);

		actual.getDetectorMode();
	}

	@Test
	public void parseFindingsFile() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testFindingsFile, actual.getFindingsFile());
	}

	@Test
	public void parseProjectSrcPathTest() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testProjectSrcPath, actual.getProjectSrcPath());
	}

	@Test
	public void parseProjectClassPathTest() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testProjectClassPath, actual.getProjectClassPath());
	}

	@Test
	public void parseMisuseSrcPathTest() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testMisuseSrcPath, actual.getMisuseSrcPath());
	}

	@Test
	public void parseMisuseClassPathTest() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testMisuseClassPath, actual.getMisuseClassPath());
	}

	@Test
	public void parsePatternsSrcPathTest() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testPatternsSrcPath, actual.getPatternsSrcPath());
	}

	@Test
	public void parsePatternsClassPathTest() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testPatternsClassPath, actual.getPatternsClassPath());
	}
	
	@Test
	public void parseDetectorMode() throws FileNotFoundException {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(DetectorMode.mineAndDetect, actual.getDetectorMode());
	}
	
	@Test(expected = IllegalArgumentException.class)
	public void throwsOnIllegalArgument() {
		ArgParser.parse(new String[] { "illegal arg", "value" });
	}
}
