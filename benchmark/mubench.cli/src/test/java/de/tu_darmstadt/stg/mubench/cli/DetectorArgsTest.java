package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.*;

import org.junit.Test;

public class DetectorArgsTest {
	@Test
	public void getProjectSrcPathTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("src", uut.projectSrcPath);
	}

	@Test
	public void getProjectClassPathTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("classes", uut.projectClassPath);
	}

	@Test
	public void getPatternsSrcPathTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("psrc", uut.patternsSrcPath);
	}

	@Test
	public void getPatternsClassPathTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("pclasses", uut.patternsClassPath);
	}

	@Test
	public void getFindingsFileTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("findings.yml", uut.findingsFile);
	}
}
