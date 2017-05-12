package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class ConvertFQNToFileNameTest {
	@Test
	public void convertsType() {
		assertEquals("p/C.java", new FullyQualifiedName("p.C").toSourceFileName());
	}
	
	@Test
	public void convertsInnerType() {
		assertEquals("p/C.java", new FullyQualifiedName("p.C$I").toSourceFileName());
	}
	
	@Test
	public void convertsGlobalType() {
		assertEquals("C.java", new FullyQualifiedName("C").toSourceFileName());
	}
}
