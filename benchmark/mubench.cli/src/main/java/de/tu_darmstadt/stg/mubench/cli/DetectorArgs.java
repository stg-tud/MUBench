package de.tu_darmstadt.stg.mubench.cli;

import java.io.FileNotFoundException;

public class DetectorArgs {
	private final String findingsFile;
	private final String runFile;
	private final String trainingSrcPath;
	private final String trainingClassPath;
	private final String targetSrcPath;
	private final String targetClassPath;
	private final DetectorMode detectorMode;

	public DetectorArgs(String findingsFile, String runFile, DetectorMode detectorMode, String trainingSrcPath,
			String trainingClassPath, String targetSrcPath, String targetClassPath) {
		this.findingsFile = findingsFile;
		this.runFile = runFile;
		this.trainingSrcPath = trainingSrcPath;
		this.trainingClassPath = trainingClassPath;
		this.targetSrcPath = targetSrcPath;
		this.targetClassPath = targetClassPath;
		this.detectorMode = detectorMode;
	}

	public String getFindingsFile() throws FileNotFoundException {
		if (findingsFile == null)
			throw new FileNotFoundException("findings file not provided");
		return findingsFile;
	}
	
	public String getRunFile() throws FileNotFoundException {
		if (runFile == null)
			throw new FileNotFoundException("run file not provided");
		return runFile;
	}

	public DetectorMode getDetectorMode() throws FileNotFoundException {
		if (detectorMode == null)
			throw new FileNotFoundException("detector mode not provided");
		return detectorMode;
	}

	public String getTrainingSrcPath() throws FileNotFoundException {
		if (trainingSrcPath == null)
			throw new FileNotFoundException("training source path not provided");
		return trainingSrcPath;
	}

	public String getTrainingClassPath() throws FileNotFoundException {
		if (trainingClassPath == null)
			throw new FileNotFoundException("training classpath not provided");
		return trainingClassPath;
	}

	public String getTargetSrcPath() throws FileNotFoundException {
		if (targetSrcPath == null)
			throw new FileNotFoundException("target source path not provided");
		return targetSrcPath;
	}

	public String getTargetClassPath() throws FileNotFoundException {
		if (targetClassPath == null)
			throw new FileNotFoundException("target classpath not provided");
		return targetClassPath;
	}

	public CodePath getTargetPath() throws FileNotFoundException {
		return new CodePath(getTargetSrcPath(), getTargetClassPath());
	}

	public CodePath getTrainingPath() throws FileNotFoundException {
		return new CodePath(getTrainingSrcPath(), getTargetClassPath());
	}

}
