package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;

import java.io.FileNotFoundException;

import org.junit.Test;

public class DetectorArgsTest {
	
	@Test
	public void getTrainingSrcPath() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "run.yml", DetectorMode.DETECT_ONLY, "src", "", "", "");
		assertEquals("src", uut.getTrainingSrcPath());
	}

	@Test
	public void getTrainingClassPath() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "run.yml", DetectorMode.DETECT_ONLY, "", "classes", "", "");
		assertEquals("classes", uut.getTrainingClassPath());
	}
	
	@Test
	public void getTargetSrcPath() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "run.yml", DetectorMode.DETECT_ONLY, "", "", "src", "");
		assertEquals("src", uut.getTargetSrcPath());
	}

	@Test
	public void getTargetClassPath() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("", "run.yml", DetectorMode.DETECT_ONLY, "", "", "", "classes");
		assertEquals("classes", uut.getTargetClassPath());
	}

	@Test
	public void getFindingsFileTest() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "run.yml", DetectorMode.DETECT_ONLY, "", "", "", "");
		assertEquals("findings.yml", uut.getFindingsFile());
	}
	
	@Test
	public void getRunFileTest() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("", "run.yml", DetectorMode.DETECT_ONLY, "", "", "", "");
		assertEquals("run.yml", uut.getRunFile());
	}
	
	@Test
	public void getDetectorModeTest() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("", "run.yml", DetectorMode.DETECT_ONLY, "", "", "", "");
		assertEquals(DetectorMode.DETECT_ONLY, uut.getDetectorMode());
	}
	
	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoFindingsFile() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs(null, null, null, null, null, null, null);
		uut.getFindingsFile();
	}
	
	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoRunFile() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs(null, null, null, null, null, null, null);
		uut.getRunFile();
	}

	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoDetectorMode() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs(null, null, null, null, null, null, null);
		uut.getDetectorMode();
	}
	
	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoTrainingSrcPath() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs(null, null, null, null, null, null, null);
		uut.getTrainingSrcPath();
	}
	
	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoTrainingClassPath() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs(null, null, null, null, null, null, null);
		uut.getTrainingClassPath();
	}
	
	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoTargetSrcPath() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs(null, null, null, null, null, null, null);
		uut.getTargetSrcPath();
	}
	
	@Test(expected = FileNotFoundException.class)
	public void throwsOnNoTargetClassPath() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs(null, null, null, null, null, null, null);
		uut.getTargetClassPath();
	}
}
