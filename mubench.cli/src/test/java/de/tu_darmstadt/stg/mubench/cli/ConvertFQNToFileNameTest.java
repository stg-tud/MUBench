package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class ConvertFQNToFileNameTest {
	@Test
	public void convertsType() {
		assertEquals("p/C.java", DetectorFinding.convertFQNtoFileName("p.C"));
	}
	
	@Test
	public void convertsInnerType() {
		assertEquals("p/C.java", DetectorFinding.convertFQNtoFileName("p.C$I"));
	}
	
	@Test
	public void convertsGlobalType() {
		assertEquals("C.java", DetectorFinding.convertFQNtoFileName("C"));
	}
}
