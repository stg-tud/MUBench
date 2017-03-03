package de.tu_darmstadt.stg.mubench.cli;

public class ArgParser {
	public static final String keyFindingsFile = "target";
	public static final String keyRunFile = "run_info";
	public static final String keyDetectorMode = "detector_mode";
	public static final String keyTrainingSrcPath = "training_src_path";
	public static final String keyTrainingClassPath = "training_classpath";
	public static final String keyTargetSrcPath = "target_src_path";
	public static final String keyTargetClassPath = "target_classpath";

	public static DetectorArgs parse(String[] args) {
		String findingsFile = null;
		String runFile = null;
		DetectorMode detectorMode = null;
		String trainingSrcPath = null;
		String trainingClassPath = null;
		String targetSrcPath = null;
		String targetClassPath = null;

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
				trainingSrcPath = next_arg;
				break;
			case keyTrainingClassPath:
				trainingClassPath = next_arg;
				break;
			case keyTargetSrcPath:
				targetSrcPath = next_arg;
				break;
			case keyTargetClassPath:
				targetClassPath = next_arg;
				break;
			case keyDetectorMode:
				if (next_arg.equals("0")) {
					detectorMode = DetectorMode.MINE_AND_DETECT;
				} else if (next_arg.equals("1")) {
					detectorMode = DetectorMode.DETECT_ONLY;
				} else {
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
		System.out.println("TrainingSrcPath : " + trainingSrcPath);
		System.out.println("TrainingClassPath : " + trainingClassPath);
		System.out.println("TargetSrcPath : " + targetSrcPath);
		System.out.println("TargetClassPath : " + targetClassPath);

		return new DetectorArgs(findingsFile, runFile, detectorMode, trainingSrcPath, trainingClassPath, 
				targetSrcPath, targetClassPath);
	}
}
