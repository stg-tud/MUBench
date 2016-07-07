package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class DetectorFindingTest {
	@Test
	public void addsFile(){
		DetectorFinding uut = new DetectorFinding("-file-", "");
		assertEquals(uut.get("file"), "-file-");		
	}
	
	@Test
	public void addsMethod() {
		DetectorFinding uut = new DetectorFinding("", "-method-");
		assertEquals(uut.get("method"), "-method-");	
	}
	
	@Test
	public void addsAdditionals() {
		DetectorFinding uut = new DetectorFinding("", "");
		uut.put("other", "value");
		assertEquals(uut.get("other"), "value");
	}
}
