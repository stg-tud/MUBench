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
		run(DetectorArgs.parse(args));
	}

	protected void run(DetectorArgs args) throws Exception {
		DetectorOutput output = new DetectorOutput(args.getFindingsFile(), args.getRunFile());
		run(args, output);
		output.write();
	}

	protected void run(DetectorArgs args, DetectorOutput output) throws Exception {
		switch (args.getDetectorMode()) {
		case DETECT_ONLY:
			detectOnly(args.getPatternPath(), args.getTargetPath(), args.getDependencyClassPath(), output);
			break;
		case MINE_AND_DETECT:
			mineAndDetect(args.getTargetPath(), args.getDependencyClassPath(), output);
			break;
		default:
			throw new IllegalArgumentException("Unsupported run mode: " + args.getDetectorMode());
		}
	}

	protected abstract void detectOnly(CodePath patternPath, CodePath targetPath, String[] dependencyClassPath, DetectorOutput output) throws Exception;

	protected abstract void mineAndDetect(CodePath trainingAndTargetPath, String[] dependencyClassPath, DetectorOutput output) throws Exception;
}
