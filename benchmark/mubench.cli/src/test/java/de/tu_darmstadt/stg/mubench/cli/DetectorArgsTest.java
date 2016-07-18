package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.*;

import java.io.FileNotFoundException;

import org.junit.Before;
import org.junit.Test;

public class DetectorArgsTest {
	
	private DetectorArgs uut;

	@Before
	public void setup() {
		uut = new DetectorArgs("findings.yml", "src", "classes", "msrc", "mclasses", "psrc", "pclasses");
	}
	
	@Test
	public void getProjectSrcPathTest() throws FileNotFoundException {
		assertEquals("src", uut.getProjectSrcPath());
	}

	@Test
	public void getProjectClassPathTest() throws FileNotFoundException {
		assertEquals("classes", uut.getProjectClassPath());
	}
	
	@Test
	public void getMisuseSrcPathTest() throws FileNotFoundException {
		assertEquals("msrc", uut.getMisuseSrcPath());
	}

	@Test
	public void getMisuseClassPathTest() throws FileNotFoundException {
		assertEquals("mclasses", uut.getMisuseClassPath());
	}

	@Test
	public void getPatternsSrcPathTest() throws FileNotFoundException {
		assertEquals("psrc", uut.getPatternsSrcPath());
	}

	@Test
	public void getPatternsClassPathTest() throws FileNotFoundException {
		assertEquals("pclasses", uut.getPatternsClassPath());
	}

	@Test
	public void getFindingsFileTest() throws FileNotFoundException {
		assertEquals("findings.yml", uut.getFindingsFile());
	}
}
