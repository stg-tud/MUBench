package de.tu_darmstadt.stg.mubench.cli;

import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

public class DetectorOutputTest {
	@Rule
	public TemporaryFolder testFolder = new TemporaryFolder();
	private DetectorOutput uut;
	private File findingsFile;
	private File runFile;

	@Before
	public void setup() throws IOException {
		findingsFile = testFolder.newFile();
		runFile = testFolder.newFile();
		uut = new DetectorOutput(findingsFile.toString(), runFile.toString());
	}

	@Test
	public void writesFinding() throws IOException {
		uut.add("file1", "method1");

		assertOutput(uut, lines("id: 0", "file: file1", "method: method1"));
	}

	@Test
	public void writesAdditionalData() throws IOException {
		DetectorFinding finding = uut.add("file", "method");
		finding.put("additional", "info");

		assertOutput(uut, lines("id: 0", "file: file", "method: method", "additional: info"));
	}

	@Test
	public void writesListData() throws IOException {
		DetectorFinding finding = uut.add("f", "m");
		finding.put("list", Arrays.asList("a", "b", "c"));

		assertOutput(uut, lines("id: 0", "file: f", "method: m", "list:", "- a", "- b", "- c"));
	}

	@Test
	public void writesMultipleFindings() throws IOException {
		uut.add("f1", "m1");
		uut.add("f2", "m2");

		assertOutput(uut, lines("id: 0", "file: f1", "method: m1", "---", "id: 1", "file: f2", "method: m2"));
	}

	@Test
	public void writesMultilineData() throws IOException {
		DetectorFinding finding = uut.add("f", "m");
		finding.put("multiline", "line1\nline2\n");

		assertOutput(uut, lines("id: 0", "file: f", "method: m", "multiline: |", "  line1", "  line2"));
	}

	@Test
	public void writesMultilineDataWithCR() throws IOException {
		DetectorFinding finding = uut.add("f", "m");
		finding.put("multiline", "line1\r\nline2\n\r");

		assertOutput(uut, lines("id: 0", "file: f", "method: m", "multiline: |", "  line1", "  line2"));
	}

	@Test
	public void writesRunInformation() throws IOException {
		uut.addRunInformation("patternfrequency", "10");
		uut.write();
		String[] expected = new String[] { "patternfrequency: '10'" };
		Path outputPath = Paths.get(runFile.getAbsolutePath());
		List<String> output = Files.readAllLines(outputPath, Charset.forName("UTF-8"));
		assertThat(output, is(lines(expected)));
	}

	private List<String> lines(String... lines) {
		return Arrays.asList(lines);
	}

	private void assertOutput(DetectorOutput detectorOutput, List<String> lines) throws IOException {
		detectorOutput.write();
		Path outputPath = Paths.get(findingsFile.getAbsolutePath());
		List<String> output = Files.readAllLines(outputPath, Charset.forName("UTF-8"));
		assertThat(output, is(lines));
	}
}
