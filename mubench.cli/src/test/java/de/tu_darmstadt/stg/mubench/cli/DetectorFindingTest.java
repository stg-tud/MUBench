package de.tu_darmstadt.stg.mubench.cli;

import static org.hamcrest.Matchers.not;
import static org.hamcrest.collection.IsEmptyIterable.emptyIterable;
import static org.hamcrest.collection.IsIterableContainingInAnyOrder.containsInAnyOrder;
import static org.hamcrest.collection.IsMapContaining.hasEntry;
import static org.junit.Assert.assertThat;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;

import org.junit.Before;
import org.junit.Test;

public class DetectorFindingTest {
	private DetectorFinding uut;

	@Before
	public void setup() {
		uut = new DetectorFinding(0, "-file-", "-method-");
	}
	
	@Test
	public void addsId() {
		assertThat(uut.getContent(), hasEntry("id", (Object) 0));
	}
	
	@Test
	public void addsFile() {
		assertThat(uut.getContent(), hasEntry("file", (Object) "-file-"));
	}

	@Test
	public void addsMethod() {
		assertThat(uut.getContent(), hasEntry("method", (Object) "-method-"));
	}

	@Test
	public void addsAdditionals() {
		uut.put("other", "value");
		assertThat(uut.getContent(), hasEntry("other", (Object) "value"));
	}
	
	@Test
	public void addsCollection() {
		uut.put("collection", Arrays.asList("a", "b", "c"));
		assertThat(uut.getContent().keySet(), not(emptyIterable()));
	}
	
	@Test
	@SuppressWarnings("unchecked")
	public void convertsCollectionToList() {
		HashSet<String> set = new HashSet<>();
		set.add("a");
		set.add("b");
		set.add("c");
		
		uut.put("collection", set);
		
		assertThat((List<String>) uut.getContent().get("collection"), containsInAnyOrder("a", "b", "c"));
	}
}
