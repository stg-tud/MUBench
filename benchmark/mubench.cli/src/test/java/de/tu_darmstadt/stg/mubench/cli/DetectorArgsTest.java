package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.*;

import org.junit.Test;

public class DetectorArgsTest {
	@Test
	public void getProjectSrcPathTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("src", uut.getProjectSrcPath());
	}

	@Test
	public void getProjectClassPathTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("classes", uut.getProjectClassPath());
	}

	@Test
	public void getPatternsSrcPathTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("psrc", uut.getPatternsSrcPath());
	}

	@Test
	public void getPatternsClassPathTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("pclasses", uut.getPatternsClassesPath());
	}

	@Test
	public void getFindingsFileTest() {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("findings.yml", uut.getFindingsFile());
	}
}
