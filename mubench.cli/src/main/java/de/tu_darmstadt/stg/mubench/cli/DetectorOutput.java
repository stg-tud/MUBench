package de.tu_darmstadt.stg.mubench.cli;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;

public class DetectorOutput {
	private final File findingsFile;
	private final File runInformationFile;
	private final List<DetectorFinding> findings;
	private final HashMap<String, Object> runInformation;

	DetectorOutput(String findingsFilePath, String runInformationFilePath) throws FileNotFoundException {
		findings = new LinkedList<>();
		runInformation = new HashMap<>();
		findingsFile = new File(findingsFilePath);
		runInformationFile = new File(runInformationFilePath);
	}

	public String getAdditionalOutputPath() throws FileNotFoundException {
		return findingsFile.getParent();
	}

	public DetectorFinding add(String file, String method) {
		DetectorFinding finding = new DetectorFinding(findings.size(), file, method);
		findings.add(finding);
		return finding;
	}

	public void addRunInformation(String key, String value) {
		runInformation.put(key, value);
	}

	@SuppressWarnings("unchecked")
	public void addRunInformation(String key, Iterable<String> values) {
		runInformation.put(key, values);
	}

	void write() throws IOException {
		writeFindings();
		writeRunInformation();
	}

	private void writeFindings() throws IOException, UnsupportedEncodingException, FileNotFoundException {
		try (Writer writer = new OutputStreamWriter(new FileOutputStream(findingsFile), "UTF-8")) {
			DumperOptions options = new DumperOptions();
			options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
			Yaml yaml = new Yaml(options);
			yaml.dumpAll(getContent(), writer);
		}
	}

	private Iterator<Map<String, Object>> getContent() {
		List<Map<String, Object>> content = new ArrayList<>();
		for (DetectorFinding finding : findings) {
			content.add(finding.getContent());
		}
		return content.iterator();
	}

	private void writeRunInformation() throws UnsupportedEncodingException, FileNotFoundException, IOException {
		try (Writer writer = new OutputStreamWriter(new FileOutputStream(runInformationFile), "UTF-8")) {
			DumperOptions options = new DumperOptions();
			options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
			Yaml yaml = new Yaml(options);
			yaml.dump(runInformation, writer);
		}
	}
}
