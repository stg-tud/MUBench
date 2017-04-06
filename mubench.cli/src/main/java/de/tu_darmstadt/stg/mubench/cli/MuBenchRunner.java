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
@SuppressWarnings("WeakerAccess")
public abstract class MuBenchRunner {
	@SuppressWarnings("unused")
	public void run(String[] args) throws Exception {
		run(DetectorArgs.parse(args));
	}

	/**
	 * Runs this runner with the given arguments.
	 */
	protected void run(DetectorArgs args) throws Exception {
		DetectorOutput output = new DetectorOutput(args.getFindingsFile(), args.getRunFile());
		run(args, output);
		output.write();
	}

	/**
	 * Runs this runner with the given arguments. Results written to output are persisted after return.
	 */
	protected void run(DetectorArgs args, DetectorOutput output) throws Exception {
		switch (args.getDetectorMode()) {
		case DETECT_ONLY:
			detectOnly(args, output);
			break;
		case MINE_AND_DETECT:
			mineAndDetect(args, output);
			break;
		default:
			throw new IllegalArgumentException("Unsupported run mode: " + args.getDetectorMode());
		}
	}

	/**
	 * Runs this detector in detect-only mode. Should use {@link DetectorArgs#getPatternPath()} to extract patterns and
	 * identify respective violations in {@link DetectorArgs#getTargetPath()}. Results written to output are persisted
	 * after return.
	 */
	protected abstract void detectOnly(DetectorArgs args, DetectorOutput output) throws Exception;

	/**
	 * Runs this detector in mine-and-detect mode. Should identify misuses in {@link DetectorArgs#getTargetPath()}. May
	 * use {@link DetectorArgs#getTargetPath()} for pattern mining. Results written to output are persisted after
	 * return.
	 */
	protected abstract void mineAndDetect(DetectorArgs args, DetectorOutput output) throws Exception;
}
