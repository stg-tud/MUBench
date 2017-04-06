package de.tu_darmstadt.stg.mubench.cli;

import java.io.FileNotFoundException;

@SuppressWarnings("WeakerAccess")
public class DetectorArgs {
	static final String keyFindingsFile = "target";
	static final String keyRunFile = "run_info";
	static final String keyDetectorMode = "detector_mode";
	static final String keyTrainingSrcPath = "training_src_path";
	static final String keyTrainingClassPath = "training_classpath";
	static final String keyTargetSrcPath = "target_src_path";
	static final String keyTargetClassPath = "target_classpath";
	static final String keyDependenciesClassPath = "dep_classpath";

	static DetectorArgs parse(String[] args) {
		String findingsFile = null;
		String runFile = null;
		DetectorMode detectorMode = null;
		String patternSrcPath = null;
		String patternClassPath = null;
		String targetSrcPath = null;
		String targetClassPath = null;
		String dependencyClassPath = null;

		for (int i = 0; i < args.length; i += 2) {
			String arg = args[i];
			String next_arg = args[i + 1];

			switch (arg) {
				case keyFindingsFile:
					findingsFile = next_arg;
					break;
				case keyRunFile:
					runFile = next_arg;
					break;
				case keyTrainingSrcPath:
					patternSrcPath = next_arg;
					break;
				case keyTrainingClassPath:
					patternClassPath = next_arg;
					break;
				case keyTargetSrcPath:
					targetSrcPath = next_arg;
					break;
				case keyTargetClassPath:
					targetClassPath = next_arg;
					break;
				case keyDependenciesClassPath:
					dependencyClassPath = next_arg;
					break;
				case keyDetectorMode:
                    switch (next_arg) {
                        case "0":
                            detectorMode = DetectorMode.MINE_AND_DETECT;
                            break;
                        case "1":
                            detectorMode = DetectorMode.DETECT_ONLY;
                            break;
                        default:
                            throw new IllegalArgumentException("Unknown detector mode " + next_arg);
                    }
					break;
				default:
					throw new IllegalArgumentException("Unknown key " + arg);
			}
		}

		System.out.println("FindingsFile : " + findingsFile);
		System.out.println("RunFile : " + runFile);
		System.out.println("DetectorMode : " + detectorMode);
		System.out.println("TrainingSrcPath : " + patternSrcPath);
		System.out.println("TrainingClassPath : " + patternClassPath);
		System.out.println("TargetSrcPath : " + targetSrcPath);
		System.out.println("TargetClassPath : " + targetClassPath);
		System.out.println("DepClassPath: " + dependencyClassPath);

		return new DetectorArgs(findingsFile, runFile, detectorMode, patternSrcPath, patternClassPath, targetSrcPath,
				targetClassPath, dependencyClassPath);
	}


	private final String findingsFile;
	private final String runFile;
	private final String patternSrcPath;
	private final String patternClassPath;
	private final String targetSrcPath;
	private final String targetClassPath;
	private final String dependencyClassPath;
	private final DetectorMode detectorMode;

	DetectorArgs(String findingsFile, String runFile, DetectorMode detectorMode, String patternSrcPath,
                 String patternClassPath, String targetSrcPath, String targetClassPath, String dependencyClassPath) {
		this.findingsFile = findingsFile;
		this.runFile = runFile;
		this.patternSrcPath = patternSrcPath;
		this.patternClassPath = patternClassPath;
		this.targetSrcPath = targetSrcPath;
		this.targetClassPath = targetClassPath;
		this.dependencyClassPath = dependencyClassPath;
		this.detectorMode = detectorMode;
	}

	String getFindingsFile() throws FileNotFoundException {
		if (findingsFile == null)
			throw new FileNotFoundException("findings file not provided");
		return findingsFile;
	}

	String getRunFile() throws FileNotFoundException {
		if (runFile == null)
			throw new FileNotFoundException("run file not provided");
		return runFile;
	}

	DetectorMode getDetectorMode() throws FileNotFoundException {
		if (detectorMode == null)
			throw new FileNotFoundException("detector mode not provided");
		return detectorMode;
	}

	String getPatternSrcPath() throws FileNotFoundException {
		if (patternSrcPath == null)
			throw new FileNotFoundException("training source path not provided");
		return patternSrcPath;
	}

	String getPatternClassPath() throws FileNotFoundException {
		if (patternClassPath == null)
			throw new FileNotFoundException("training classpath not provided");
		return patternClassPath;
	}

	String getTargetSrcPath() throws FileNotFoundException {
		if (targetSrcPath == null)
			throw new FileNotFoundException("target source path not provided");
		return targetSrcPath;
	}

	String getTargetClassPath() throws FileNotFoundException {
		if (targetClassPath == null)
			throw new FileNotFoundException("target classpath not provided");
		return targetClassPath;
	}

    /**
     * @return path to the source and class files to check for misuses. The code under this path may also be used for
     * training the detector.
     * @throws FileNotFoundException if either path was not provided in the runner invocation
     */
	public CodePath getTargetPath() throws FileNotFoundException {
		return new CodePath(getTargetSrcPath(), getTargetClassPath());
	}

    /**
     * @return path to the source and class files of the patterns for particular misuses. Should be used to extract the
     * patterns in detect-only mode.
     * @throws FileNotFoundException if either path was not provided in the runner invocation, e.g., if the runner is
     * invoked in mine-and-detect mode.
     */
	public CodePath getPatternPath() throws FileNotFoundException {
		return new CodePath(getPatternSrcPath(), getPatternClassPath());
	}

    /**
     * @return a classpath referencing the dependencies of the code in the {@link #getTargetPath()}.
     */
    public String[] getDependencyClassPath() throws FileNotFoundException {
        return dependencyClassPath == null ? new String[0] : dependencyClassPath.split(":");
    }
}
