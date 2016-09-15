package de.tu_darmstadt.stg.mubench.cli;

/**
 * Implement a concrete runner like this:
 * <pre><code>
 * public class XYRunner extends MuBenchRunner {
 *   public static void main(String[] args) {
 *   	new XYRunner().run(args);
 *   }
 *   
 *   // Run-Mode Implementations
 *   ...
 * }
 * </code></pre>
 */
public abstract class MuBenchRunner {
	public void run(String[] args) throws Exception {
		run(ArgParser.parse(args));
	}

	protected void run(DetectorArgs args) throws Exception {
		DetectorOutput output = new DetectorOutput(args.getFindingsFile(), args.getRunFile());
		run(args.getDetectorMode(), args, output);
		output.write();
	}

	protected void run(DetectorMode detectorMode, DetectorArgs args, DetectorOutput output) throws Exception {
		switch (detectorMode) {
		case DETECT_ONLY:
			detectOnly(args.getTrainingPath(), args.getTargetPath(), output);
			break;
		case MINE_AND_DETECT:
			mineAndDetect(args.getTrainingPath(), output);
			break;
		default:
			throw new IllegalArgumentException("Unsupported runmode: " + detectorMode);
		}
	}

	protected abstract void detectOnly(CodePath patternPath, CodePath targetPath, DetectorOutput output) throws Exception;

	protected abstract void mineAndDetect(CodePath trainingAndTargetPath, DetectorOutput output) throws Exception;
}
