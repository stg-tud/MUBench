package de.tu_darmstadt.stg.mubench.cli;

public class DetectorArgs {

	public final String findingsFile;
	public final String projectSrcPath;
	public final String projectClassPath;
	public final String patternsSrcPath;
	public final String patternsClassPath;

	public DetectorArgs(String findingsFile, String projectSrc, String projectClasses, String patternsSrc,
			String patternsClasses) {
		this.findingsFile = findingsFile;
		this.projectSrcPath = projectSrc;
		this.projectClassPath = projectClasses;
		this.patternsSrcPath = patternsSrc;
		this.patternsClassPath = patternsClasses;
	}

}
