package de.tu_darmstadt.stg.mubench.cli;

import java.io.FileNotFoundException;

public class DetectorArgs {
	private final String findingsFile;
	private final String projectSrcPath;
	private final String projectClassPath;
	private final String misuseSrcPath;
	private final String misuseClassPath;
	private final String patternsSrcPath;
	private final String patternsClassPath;

	public DetectorArgs(String findingsFile, String projectSrc, String projectClasses, String misuseSrc, String misuseClasses, String patternsSrc,
			String patternsClasses) {
		this.findingsFile = findingsFile;
		this.projectSrcPath = projectSrc;
		this.projectClassPath = projectClasses;
		this.misuseSrcPath = misuseSrc;
		this.misuseClassPath = misuseClasses;
		this.patternsSrcPath = patternsSrc;
		this.patternsClassPath = patternsClasses;
	}

	public String getFindingsFile() throws FileNotFoundException {
		if (findingsFile == null)
			throw new FileNotFoundException("findings file not provided");
		return findingsFile;
	}
	
	public String getProjectSrcPath() throws FileNotFoundException {
		if (projectSrcPath == null)
			throw new FileNotFoundException("project source path not provided");
		return projectSrcPath;
	}
	
	public String getProjectClassPath() throws FileNotFoundException {
		if (projectClassPath == null)
			throw new FileNotFoundException("project classpath not provided");
		return projectClassPath;
	}
	
	public String getMisuseSrcPath() throws FileNotFoundException {
		if (misuseSrcPath == null)
			throw new FileNotFoundException("misuse source path not provided");
		return misuseSrcPath;
	}
	
	public String getMisuseClassPath() throws FileNotFoundException {
		if (misuseClassPath == null)
			throw new FileNotFoundException("misuse classpath not provided");
		return misuseClassPath;
	}
	
	public String getPatternsSrcPath() throws FileNotFoundException {
		if (patternsSrcPath == null)
			throw new FileNotFoundException("patterns source path not provided");
		return patternsSrcPath;
	}
	
	public String getPatternsClassPath() throws FileNotFoundException {
		if (patternsClassPath == null)
			throw new FileNotFoundException("patterns classpath not provided");
		return patternsClassPath;
	}

}
