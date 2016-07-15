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

	@Before
	public void setup() throws IOException {
		findingsFile = testFolder.newFile();
		uut = new DetectorOutput(findingsFile.toString());
	}
	
	@Test
	public void writesFinding() throws IOException {
		uut.add(new DetectorFinding("file1", "method1"));
		
		assertOutput(uut, lines("file: file1", "method: method1"));
	}
	
	@Test
	public void writesAdditionalData() throws IOException {
		DetectorFinding finding = new DetectorFinding("file", "method");
		finding.put("additional", "info");
		uut.add(finding);
		
		assertOutput(uut, lines("file: file", "method: method", "additional: info"));
	}
	
	@Test
	public void writesListData() throws IOException {
		DetectorFinding finding = new DetectorFinding("f", "m");
		finding.put("list", Arrays.asList("a", "b", "c"));
		uut.add(finding);
		
		assertOutput(uut, lines("file: f", "method: m", "list:", "- a", "- b", "- c"));
	}
	
	@Test
	public void writesMultipleFindings() throws IOException {
		uut.add(new DetectorFinding("f1", "m1"));
		uut.add(new DetectorFinding("f2", "m2"));

		assertOutput(uut, lines("file: f1", "method: m1", "---", "file: f2", "method: m2"));
	}
	
	@Test
	public void writesMultilineData() throws IOException {
		DetectorFinding finding = new DetectorFinding("f", "m");
		finding.put("multiline", "line1\nline2\n");
		uut.add(finding);
		
		assertOutput(uut, lines("file: f", "method: m", "multiline: |", "  line1", "  line2"));
	}
	
	@Test
	public void writesMultilineDataWithCR() throws IOException {
		DetectorFinding finding = new DetectorFinding("f", "m");
		finding.put("multiline", "line1\r\nline2\n\r");
		uut.add(finding);
		
		assertOutput(uut, lines("file: f", "method: m", "multiline: |", "  line1", "  line2"));
	}
	
	private List<String> lines(String...lines) {
		return Arrays.asList(lines);
	}

	private void assertOutput(DetectorOutput detectorOutput, List<String> lines) throws IOException {
		detectorOutput.write();
		Path outputPath = Paths.get(findingsFile.getAbsolutePath());
		List<String> output = Files.readAllLines(outputPath, Charset.forName("UTF-8"));
		assertThat(output, is(lines));
	}
}
