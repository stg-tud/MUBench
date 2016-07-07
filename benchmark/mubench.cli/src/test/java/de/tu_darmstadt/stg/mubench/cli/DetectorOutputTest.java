package de.tu_darmstadt.stg.mubench.cli;

import static org.hamcrest.collection.IsIterableContainingInOrder.contains;
import static org.junit.Assert.assertThat;

import java.io.File;
import java.io.IOException;
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

		DetectorFinding finding1 = new DetectorFinding("file1", "method1");
		DetectorFinding finding2 = new DetectorFinding("file1", "method2");
		finding1.put("additional", "info");
		finding2.put("other", "info");
		List<DetectorFinding> findings = Arrays.asList(finding1, finding2);

		DetectorOutput.write(findingsFile, findings);

		List<String> actualLines = Files.readAllLines(findingsFile.toPath());
		assertThat(actualLines, contains("file: file1", "method: method1", "additional: info", "---", "other: info", "file: file1",
				"method: method2"));
	}
}
