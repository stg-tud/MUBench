package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertEquals;
import static org.hamcrest.collection.IsMapContaining.hasEntry;
import static org.junit.Assert.assertThat;

import org.junit.Test;

public class DetectorFindingTest {
	@Test
	public void addsFile() {
		DetectorFinding uut = new DetectorFinding("-file-", null);
		assertThat(uut.getContent(), hasEntry("file", "-file-"));
		assertEquals(1, uut.getContent().size());
	}

	@Test
	public void addsMethod() {
		DetectorFinding uut = new DetectorFinding(null, "-method-");
		assertThat(uut.getContent(), hasEntry("method", "-method-"));
		assertEquals(1, uut.getContent().size());
	}

	@Test
	public void addsAdditionals() {
		DetectorFinding uut = new DetectorFinding(null, null);
		uut.put("other", "value");
		assertThat(uut.getContent(), hasEntry("other", "value"));
		assertEquals(1, uut.getContent().size());
	}
}
