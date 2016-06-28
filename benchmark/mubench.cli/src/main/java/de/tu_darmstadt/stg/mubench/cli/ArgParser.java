package de.tu_darmstadt.stg.mubench.cli;

public class ArgParser {
	public static final String keyFindingsFile = "target";
	public static final String keyProjectSrcPath = "src";
	public static final String keyProjectClassPath = "classpath";
	public static final String keyPatternsSrcPath = "src_patterns";
	public static final String keyPatternsClassPath = "classpath_patterns";

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

		System.out.println("FindingsFile : " + findingsFile);
		System.out.println("ProjectSrcPath : " + projectSrcPath);
		System.out.println("ProjectClassPath : " + projectClassPath);
		System.out.println("PatternsSrcPath : " + patternsSrcPath);
		System.out.println("PatternsClassPath : " + patternsClassPath);
		
		
		return new DetectorArgs(findingsFile, projectSrcPath, projectClassPath, patternsSrcPath, patternsClassPath);
	}
}
