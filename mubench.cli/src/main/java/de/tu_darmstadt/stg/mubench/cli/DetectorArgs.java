package de.tu_darmstadt.stg.mubench.cli;

import java.io.FileNotFoundException;
import java.nio.file.Path;
import java.nio.file.Paths;

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
		String correctUsageSrcPath = null;
		String correctUsageClassPath = null;
		String[] targetSrcPaths = null;
		String[] targetClassPaths = null;
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
					correctUsageSrcPath = next_arg;
					break;
				case keyTrainingClassPath:
					correctUsageClassPath = next_arg;
					break;
				case keyTargetSrcPath:
					targetSrcPaths = next_arg.split(":");
					break;
				case keyTargetClassPath:
					targetClassPaths = next_arg.split(":");
					break;
				case keyDependenciesClassPath:
					dependencyClassPath = next_arg;
					break;
				case keyDetectorMode:
                    detectorMode = DetectorMode.fromCode(next_arg);
					break;
				default:
					throw new IllegalArgumentException("Unknown key " + arg);
			}
		}

		return new DetectorArgs(findingsFile, runFile, detectorMode, correctUsageSrcPath, correctUsageClassPath, targetSrcPaths,
				targetClassPaths, dependencyClassPath);
	}


	private final String findingsFile;
	private final String runInfoFile;
	private final String correctUsageSrcPath;
	private final String correctUsageClassPath;
	private final String[] targetSrcPaths;
	private final String[] targetClassPaths;
	private final String dependencyClassPath;
	private final DetectorMode detectorMode;

	DetectorArgs(String findingsFile, String runInfoFile, DetectorMode detectorMode, String correctUsageSrcPath,
				 String correctUsageClassPath, String[] targetSrcPaths, String[] targetClassPaths, String dependencyClassPath) {
		this.findingsFile = findingsFile;
		this.runInfoFile = runInfoFile;
		this.correctUsageSrcPath = correctUsageSrcPath;
		this.correctUsageClassPath = correctUsageClassPath;
		this.targetSrcPaths = targetSrcPaths;
		this.targetClassPaths = targetClassPaths;
		this.dependencyClassPath = dependencyClassPath;
		this.detectorMode = detectorMode;
	}

	Path getFindingsFile() throws FileNotFoundException {
		if (findingsFile == null)
			throw new FileNotFoundException("findings file not provided");
		return Paths.get(findingsFile);
	}

	Path getRunInfoFile() throws FileNotFoundException {
		if (runInfoFile == null)
			throw new FileNotFoundException("run file not provided");
		return Paths.get(runInfoFile);
	}

	/**
	 * @return directory to write additional output to, e.g., for debugging purposes.
	 */
	@SuppressWarnings("unused")
	public Path getAdditionalOutputPath() throws FileNotFoundException {
		return getFindingsFile().getParent();
	}

	DetectorMode getDetectorMode() throws FileNotFoundException {
		if (detectorMode == null)
			throw new FileNotFoundException("detector mode not provided");
		return detectorMode;
	}

	/**
	 * @return path to the source files of the correctUsage for a particular misuse. Should be used to extract the
	 * correctUsages in detect-only mode.
	 * @throws FileNotFoundException if the path was not provided in the runner invocation, e.g., if the runner is
	 * invoked in mine-and-detect mode.
	 */
	public String getPatternSrcPath() throws FileNotFoundException {
		if (correctUsageSrcPath == null)
			throw new FileNotFoundException("training source path not provided");
		return correctUsageSrcPath;
	}

	/**
	 * @return path to the class files of the correctUsages for a particular misuse. Should be used to extract the
	 * correctUsages in detect-only mode.
	 * @throws FileNotFoundException if the path was not provided in the runner invocation, e.g., if the runner is
	 * invoked in mine-and-detect mode.
	 */
	public String getPatternClassPath() throws FileNotFoundException {
		if (correctUsageClassPath == null)
			throw new FileNotFoundException("training classpath not provided");
		return correctUsageClassPath;
	}


	/**
	 * @return paths to the source files to check for misuses. The code under these path may also be used for
	 * training the detector.
	 * @throws FileNotFoundException if the paths were not provided in the runner invocation
	 */
	public String[] getTargetSrcPaths() throws FileNotFoundException {
		if (targetSrcPaths == null)
			throw new FileNotFoundException("target source path not provided");
		return targetSrcPaths;
	}

	/**
	 * @return paths to the class files to check for misuses. The code under these path may also be used for
	 * training the detector.
	 * @throws FileNotFoundException if the paths were not provided in the runner invocation
	 */
	public String[] getTargetClassPaths() throws FileNotFoundException {
		if (targetClassPaths == null)
			throw new FileNotFoundException("target classpath not provided");
		return targetClassPaths;
	}

    /**
     * @return a classpath referencing the dependencies of the code in the {@link #getTargetPath()}.
     */
    public String[] getDependencyClassPath() throws FileNotFoundException {
        return dependencyClassPath == null ? new String[0] : dependencyClassPath.split(":");
    }
}
