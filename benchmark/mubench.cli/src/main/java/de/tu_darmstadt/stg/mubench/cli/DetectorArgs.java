package de.tu_darmstadt.stg.mubench.cli;

public class DetectorArgs {

	private final String findingsFile;
	private final String projectSrc;
	private final String projectClasses;
	private final String patternsSrc;
	private final String patternsClasses;

	public DetectorArgs(String findingsFile, String projectSrc, String projectClasses, String patternsSrc, String patternsClasses) {
		this.findingsFile = findingsFile;
		this.projectSrc = projectSrc;
		this.projectClasses = projectClasses;
		this.patternsSrc = patternsSrc;
		this.patternsClasses = patternsClasses;
	}

	public String getProjectSrcPath() {
		return projectSrc;
	}

	public String getProjectClassPath() {
		return projectClasses;
	}

	public String getPatternsSrcPath() {
		return patternsSrc;
	}

	public String getPatternsClassesPath() {
		return patternsClasses;
	}

	public String getFindingsFile() {
		return findingsFile;
	}

}
