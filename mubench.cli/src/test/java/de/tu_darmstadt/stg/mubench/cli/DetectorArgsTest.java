package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;

import java.io.FileNotFoundException;
import java.nio.file.Paths;

import org.junit.Test;

public class DetectorArgsTest {

	@Test
	public void parsesFindingsFile() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs.parse(new String[] { DetectorArgs.keyFindingsFile, "findings.yml" });
		assertEquals(Paths.get("findings.yml"), actual.getFindingsFile());
	}
	
	@Test
	public void parsesRunFile() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs.parse(new String[] { DetectorArgs.keyRunFile, "run.yml" });
		assertEquals(Paths.get("run.yml"), actual.getRunInfoFile());
	}

    @Test
    public void parsesDetectOnlyMode() throws FileNotFoundException {
        DetectorArgs actual = DetectorArgs.parse(new String[] { DetectorArgs.keyDetectorMode, "1" });
        assertEquals(DetectorMode.DETECT_ONLY, actual.getDetectorMode());
    }

	@Test
	public void parsesMineAndDetectMode() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs.parse(new String[] { DetectorArgs.keyDetectorMode, "0" });
		assertEquals(DetectorMode.MINE_AND_DETECT, actual.getDetectorMode());
	}

	@Test
	public void parsesTrainingPaths() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs.parse(
				new String[] { DetectorArgs.keyTrainingSrcPath, "psrc", DetectorArgs.keyTrainingClassPath, "pclasspath" });

        assertEquals("psrc", actual.getTrainingSrcPaths()[0]);
		assertEquals("pclasspath", actual.getTrainingClassPath().getClasspath());
	}

	@Test
	public void parsesTargetPath() throws FileNotFoundException {
		DetectorArgs actual = DetectorArgs
				.parse(new String[] { DetectorArgs.keyTargetSrcPath, "msrc", DetectorArgs.keyTargetClassPath, "mclasspath" });

        String[] targetSrcPaths = actual.getTargetSrcPaths();
        ClassPath targetClassPaths = actual.getTargetClassPath();
        assertEquals("msrc", targetSrcPaths[0]);
		assertEquals("mclasspath", targetClassPaths.getClasspath());
	}

	@Test
    public void parsesTargetPaths() throws FileNotFoundException {
        DetectorArgs actual = DetectorArgs
                .parse(new String[] { DetectorArgs.keyTargetSrcPath, "msrc1:msrc2",
                                      DetectorArgs.keyTargetClassPath, "mclasspath1:mclasspath2" });

        String[] targetSrcPaths = actual.getTargetSrcPaths();
        ClassPath targetClassPath = actual.getTargetClassPath();
        assertEquals("msrc1", targetSrcPaths[0]);
        assertEquals("msrc2", targetSrcPaths[1]);
        assertEquals("mclasspath1:mclasspath2", targetClassPath.getClasspath());
    }

	@Test
	public void parsesDependenciesClassPath() throws Exception {
		DetectorArgs actual = DetectorArgs.parse(new String[]{DetectorArgs.keyDependenciesClassPath, "foo:bar"});
		assertEquals("foo:bar", actual.getDependencyClassPath().getClasspath());
	}

	@Test(expected = IllegalArgumentException.class)
	public void throwsOnIllegalArgument() {
        DetectorArgs.parse(new String[] { "illegal arg", "value" });
	}

    @Test(expected = FileNotFoundException.class)
    public void throwsOnNoFindingsFile() throws FileNotFoundException {
        DetectorArgs.parse(new String[0]).getFindingsFile();
    }

    @Test(expected = FileNotFoundException.class)
    public void throwsOnNoRunFile() throws FileNotFoundException {
        DetectorArgs.parse(new String[0]).getRunInfoFile();
    }

    @Test(expected = FileNotFoundException.class)
    public void throwsOnNoDetectorMode() throws FileNotFoundException {
        DetectorArgs.parse(new String[0]).getDetectorMode();
    }

    @Test(expected = FileNotFoundException.class)
    public void throwsOnNoTrainingSrcPath() throws FileNotFoundException {
        DetectorArgs.parse(new String[0]).getTrainingSrcPaths();
    }

    @Test(expected = FileNotFoundException.class)
    public void throwsOnNoTrainingClassPath() throws FileNotFoundException {
        DetectorArgs.parse(new String[0]).getTrainingClassPath();
    }

    @Test(expected = FileNotFoundException.class)
    public void throwsOnNoTargetSrcPath() throws FileNotFoundException {
        DetectorArgs.parse(new String[0]).getTargetSrcPaths();
    }

    @Test(expected = FileNotFoundException.class)
    public void throwsOnNoTargetClassPath() throws FileNotFoundException {
        DetectorArgs.parse(new String[0]).getTargetClassPath();
    }

    @Test
    public void noDependencyClassPath() {
        DetectorArgs actual = DetectorArgs.parse(new String[0]);
        assertEquals("", actual.getDependencyClassPath().getClasspath());
    }
}
