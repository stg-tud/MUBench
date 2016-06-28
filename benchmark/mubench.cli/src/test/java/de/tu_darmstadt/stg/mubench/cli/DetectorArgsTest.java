package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.*;

import java.io.FileNotFoundException;

import org.junit.Test;

public class DetectorArgsTest {
	@Test
	public void getProjectSrcPathTest() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("src", uut.getProjectSrcPath());
	}

	@Test
	public void getProjectClassPathTest() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("classes", uut.getProjectClassPath());
	}

	@Test
	public void getPatternsSrcPathTest() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("psrc", uut.getPatternsSrcPath());
	}

	@Test
	public void getPatternsClassPathTest() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("pclasses", uut.getPatternsClassPath());
	}

	@Test
	public void getFindingsFileTest() throws FileNotFoundException {
		DetectorArgs uut = new DetectorArgs("findings.yml", "src", "classes", "psrc", "pclasses");
		assertEquals("findings.yml", uut.getFindingsFile());
	}
}
