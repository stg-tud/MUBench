package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import java.io.FileNotFoundException;

import org.junit.Test;

public class DetectorArgsTest {

	private DetectorArgs FULL_ARGS = new DetectorArgs("findings.yml", "run.yml", DetectorMode.DETECT_ONLY,
			"/tr/src", "/tr/classes", "/ta/src", "/ta/classes", "-dep:classpath-");

	private DetectorArgs EMPTY_ARGS = new DetectorArgs(null, null, null, null, null, null, null, null);

	@Test
	public void getTrainingSrcPath() throws FileNotFoundException {
		assertEquals("/tr/src", FULL_ARGS.getPatternSrcPath());
	}

	@Test
	public void getTrainingClassPath() throws FileNotFoundException {
		assertEquals("/tr/classes", FULL_ARGS.getPatternClassPath());
	}

	@Test
	public void getTargetSrcPath() throws FileNotFoundException {
		assertEquals("/ta/src", FULL_ARGS.getTargetSrcPath());
	}

	@Test
	public void getTargetClassPath() throws FileNotFoundException {
		assertEquals("/ta/classes", FULL_ARGS.getTargetClassPath());
	}

	@Test
	public void getDepClassPath() throws FileNotFoundException {
		assertArrayEquals(new String[] {"-dep", "classpath-"}, FULL_ARGS.getDependencyClassPath());
	}

	@Test
	public void getFindingsFileTest() throws FileNotFoundException {
		assertEquals("findings.yml", FULL_ARGS.getFindingsFile());
	}

	@Test
	public void getRunFileTest() throws FileNotFoundException {
		assertEquals("run.yml", FULL_ARGS.getRunFile());
	}

	@Test
	public void getDetectorModeTest() throws FileNotFoundException {
		assertEquals(DetectorMode.DETECT_ONLY, FULL_ARGS.getDetectorMode());
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoFindingsFile() throws FileNotFoundException {
		EMPTY_ARGS.getFindingsFile();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoRunFile() throws FileNotFoundException {
		EMPTY_ARGS.getRunFile();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoDetectorMode() throws FileNotFoundException {
		EMPTY_ARGS.getDetectorMode();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoTrainingSrcPath() throws FileNotFoundException {
		EMPTY_ARGS.getPatternSrcPath();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoTrainingClassPath() throws FileNotFoundException {
		EMPTY_ARGS.getPatternClassPath();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoTargetSrcPath() throws FileNotFoundException {
		EMPTY_ARGS.getTargetSrcPath();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoTargetClassPath() throws FileNotFoundException {
		EMPTY_ARGS.getTargetClassPath();
	}

	@Test
	public void noDependencyClassPath() throws FileNotFoundException {
		assertArrayEquals(new String[0], EMPTY_ARGS.getDependencyClassPath());
	}
}
