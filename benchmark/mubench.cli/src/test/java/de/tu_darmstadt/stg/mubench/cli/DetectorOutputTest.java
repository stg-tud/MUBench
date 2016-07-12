package de.tu_darmstadt.stg.mubench.cli;

import static org.hamcrest.collection.IsIterableContainingInOrder.contains;
import static org.junit.Assert.assertThat;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.List;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

public class DetectorOutputTest {
	@Rule
	public TemporaryFolder testFolder = new TemporaryFolder();

	@Test
	public void writesFindings() throws IOException {
		File findingsFile = testFolder.newFile();
		DetectorOutput uut = new DetectorOutput(new DetectorArgs(findingsFile.toString(), "", "", "", ""));

		DetectorFinding finding1 = new DetectorFinding("file1", "method1");
		DetectorFinding finding2 = new DetectorFinding("file2", "method2");
		finding1.put("additional", "info");
		finding2.put("other", "info");
		finding2.put("collection", Arrays.asList("a", "b", "c"));
		List<DetectorFinding> findings = Arrays.asList(finding1, finding2);

		uut.addAll(findings);
		uut.write();

		List<String> actualLines = Files.readAllLines(findingsFile.toPath(), Charset.forName("UTF-8"));
		assertThat(actualLines, contains("file: file1", "method: method1", "additional: info", "---",
				"file: file2", "method: method2", "other: info", "collection:", "- a", "- b", "- c"));
	}
}
