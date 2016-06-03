package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

import org.junit.Test;

public class ArgParserTest {
	private static final String testFindingsFile = "findings.yml";
	private static final String testProjectSrcPath = "src";
	private static final String testProjectClassPath = "classpath";
	private static final String testPatternsSrcPath = "psrc";
	private static final String testPatternsClassPath = "pclasspath";

	String[] testArgs = new String[] { Keys.keyFindingsFile(), testFindingsFile, Keys.keyProjectSrc(),
			testProjectSrcPath, Keys.keyProjectClassPath(), testProjectClassPath, Keys.keyPatternsSrc(),
			testPatternsSrcPath, Keys.keyPatternsClassPath(), testPatternsClassPath };
	
	@Test
	public void defaultNull() {
		String[] empty_args = new String[0];
		DetectorArgs actual = ArgParser.parse(empty_args);
		assertNull(actual.findingsFile);
		assertNull(actual.projectSrcPath);
		assertNull(actual.projectClassPath);
		assertNull(actual.patternsSrcPath);
		assertNull(actual.patternsClassPath);		
	}

	@Test
	public void parseFindingsFile() {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testFindingsFile, actual.findingsFile);
	}

	@Test
	public void parseProjectSrcPathTest() {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testProjectSrcPath, actual.projectSrcPath);
	}

	@Test
	public void parseProjectClassPathTest() {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testProjectClassPath, actual.projectClassPath);
	}

	@Test
	public void parsePatternsSrcPathTest() {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testPatternsSrcPath, actual.patternsSrcPath);
	}

	@Test
	public void parsePatternsClassPathTest() {
		DetectorArgs actual = ArgParser.parse(testArgs);
		assertEquals(testPatternsClassPath, actual.patternsClassPath);
	}
	
	@Test(expected = IllegalArgumentException.class)
	public void throwsOnIllegalArgument() {
		ArgParser.parse(new String[]{"illegal arg", "value"});
	}

	private final static class Keys extends ArgParser {

		public static String keyFindingsFile() {
			return keyFindingsFile;
		}

		public static String keyProjectSrc() {
			return keyProjectSrcPath;
		}

		public static String keyProjectClassPath() {
			return keyProjectClassPath;
		}

		public static String keyPatternsSrc() {
			return keyPatternsSrcPath;
		}

		public static String keyPatternsClassPath() {
			return keyPatternsClassPath;
		}
	}
}
