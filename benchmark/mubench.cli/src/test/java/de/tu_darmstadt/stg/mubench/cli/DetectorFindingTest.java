package de.tu_darmstadt.stg.mubench.cli;

import static org.hamcrest.Matchers.not;
import static org.hamcrest.collection.IsEmptyIterable.emptyIterable;
import static org.hamcrest.collection.IsMapContaining.hasEntry;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;

import java.util.Arrays;

import org.junit.Test;

public class DetectorFindingTest {
	@Test
	public void addsFile() {
		DetectorFinding uut = new DetectorFinding("-file-", null);
		assertThat(uut.getContent(), hasEntry((Object) "file", (Object) "-file-"));
		assertEquals(1, uut.getContent().size());
	}

	@Test
	public void addsMethod() {
		DetectorFinding uut = new DetectorFinding(null, "-method-");
		assertThat(uut.getContent(), hasEntry((Object) "method", (Object) "-method-"));
		assertEquals(1, uut.getContent().size());
	}

	@Test
	public void addsAdditionals() {
		DetectorFinding uut = new DetectorFinding(null, null);
		uut.put("other", "value");
		assertThat(uut.getContent(), hasEntry((Object) "other", (Object) "value"));
		assertEquals(1, uut.getContent().size());
	}
	
	@Test
	public void addsCollection() {
		DetectorFinding uut = new DetectorFinding(null, null);
		uut.put("collection", Arrays.asList("a", "b", "c"));
		assertThat(uut.getContent().keySet(), not(emptyIterable()));
	}
}
