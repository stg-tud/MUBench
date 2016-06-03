package de.tu_darmstadt.stg.mubench.cli;

public class ArgParser {
	protected static final String keyFindingsFile = "target";
	protected static final String keyProjectSrcPath = "src";
	protected static final String keyProjectClassPath = "classpath";
	protected static final String keyPatternsSrcPath = "src_patterns";
	protected static final String keyPatternsClassPath = "classpath_patterns";

	public static DetectorArgs parse(String[] args) {
		String findingsFile = null;
		String projectSrcPath = null;
		String projectClassPath = null;
		String patternsSrcPath = null;
		String patternsClassPath = null;

		for (int i = 0; i < args.length; i += 2) {
			String arg = args[i];
			String next_arg = args[i + 1];

			switch (arg) {
			case keyFindingsFile:
				findingsFile = next_arg;
				break;
			case keyProjectSrcPath:
				projectSrcPath = next_arg;
				break;
			case keyProjectClassPath:
				projectClassPath = next_arg;
				break;
			case keyPatternsSrcPath:
				patternsSrcPath = next_arg;
				break;
			case keyPatternsClassPath:
				patternsClassPath = next_arg;
				break;
			default:
				throw new IllegalArgumentException("Unknown key " + arg);
			}
		}

		return new DetectorArgs(findingsFile, projectSrcPath, projectClassPath, patternsSrcPath, patternsClassPath);
	}
}
