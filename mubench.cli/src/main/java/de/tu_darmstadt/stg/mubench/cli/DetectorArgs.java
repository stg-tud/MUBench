package de.tu_darmstadt.stg.mubench.cli;

import java.io.FileNotFoundException;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Represents the input passed from the MUBench Pipeline to a runner, as input to the detector.
 */
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
		String[] trainingSrcPaths = null;
		String trainingClassPath = null;
		String[] targetSrcPaths = null;
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
					trainingSrcPaths = next_arg.split(":");
					break;
				case keyTrainingClassPath:
					trainingClassPath = next_arg;
					break;
				case keyTargetSrcPath:
					targetSrcPaths = next_arg.split(":");
					break;
				case keyTargetClassPath:
					targetClassPath = next_arg;
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

		return new DetectorArgs(findingsFile, runFile, detectorMode, trainingSrcPaths, trainingClassPath, targetSrcPaths,
				targetClassPath, dependencyClassPath);
	}


	private final String findingsFile;
	private final String runInfoFile;
	private final String[] trainingSrcPaths;
	private final String trainingClassPath;
	private final String[] targetSrcPaths;
	private final String targetClassPath;
	private final String dependencyClassPath;
	private final DetectorMode detectorMode;

	DetectorArgs(String findingsFile, String runInfoFile, DetectorMode detectorMode, String[] trainingSrcPaths,
				 String trainingClassPath, String[] targetSrcPaths, String targetClassPath, String dependencyClassPath) {
		this.findingsFile = findingsFile;
		this.runInfoFile = runInfoFile;
		this.trainingSrcPaths = trainingSrcPaths;
		this.trainingClassPath = trainingClassPath;
		this.targetSrcPaths = targetSrcPaths;
		this.targetClassPath = targetClassPath;
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
     * @throws FileNotFoundException if the directory was not provided
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
	 * @return paths to the source files that may be used to train the detector, i.e., the path to the correct usage in
     * detect-only mode. No training data is provided in mine-and-detect mode. Here, {@link #getTargetSrcPaths()} should
     * be used for training instead.
	 * @throws FileNotFoundException if the path was not provided in the runner invocation, e.g., if the runner is
	 * invoked in mine-and-detect mode.
	 */
	public String[] getTrainingSrcPaths() throws FileNotFoundException {
		if (trainingSrcPaths == null)
			throw new FileNotFoundException("no training source path provided");
		return trainingSrcPaths;
	}

	/**
	 * @return path to the class files that may be used to train the detector, i.e., the path to the correct usage in
     * detect-only mode. No training data is provided in mine-and-detect mode. Here, {@link #getTargetClassPath()}
     * should be used for training instead.
	 * @throws FileNotFoundException if the path was not provided in the runner invocation, e.g., if the runner is
	 * invoked in mine-and-detect mode.
	 */
	public ClassPath getTrainingClassPath() throws FileNotFoundException {
		if (trainingClassPath == null)
			throw new FileNotFoundException("no training classpath provided");
		return new ClassPath(trainingClassPath);
	}


	/**
	 * @return paths to the source files to check for misuses. The code under these path may also be used for
	 * training the detector.
	 * @throws FileNotFoundException if the paths were not provided in the runner invocation
	 */
	public String[] getTargetSrcPaths() throws FileNotFoundException {
		if (targetSrcPaths == null)
			throw new FileNotFoundException("no target source path provided");
		return targetSrcPaths;
	}

	/**
	 * @return paths to the class files to check for misuses. The code under these path may also be used for
	 * training the detector.
	 * @throws FileNotFoundException if the paths were not provided in the runner invocation
	 */
	public ClassPath getTargetClassPath() throws FileNotFoundException {
		if (targetClassPath == null)
			throw new FileNotFoundException("no target classpath provided");
		return new ClassPath(targetClassPath);
	}

    /**
     * @return a classpath referencing the dependencies of the target code
     * ({@link #getTargetSrcPaths()}/{@link #getTargetClassPath()}).
     */
    public ClassPath getDependencyClassPath() {
        return dependencyClassPath == null ? new ClassPath("") : new ClassPath(dependencyClassPath);
    }
}
