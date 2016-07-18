package de.tu_darmstadt.stg.mubench.cli;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;

public class DetectorOutput {
	private final File findingsFile;
	private final List<DetectorFinding> findings;

	public DetectorOutput(String findingsFilePath) throws FileNotFoundException {
		findings = new LinkedList<>();
		findingsFile = new File(findingsFilePath);
	}

	public DetectorFinding add(String file, String method) {
		DetectorFinding finding = new DetectorFinding(findings.size(), file, method);
		findings.add(finding);
		return finding;
	}

	public void write() throws IOException {
		try (Writer writer = new OutputStreamWriter(new FileOutputStream(findingsFile), "UTF-8")) {
			DumperOptions options = new DumperOptions();
			options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
			Yaml yaml = new Yaml(options);
			yaml.dumpAll(getContent(), writer);
		}
	}
	
	private Iterator<Map<String, Object>> getContent() {
		return findings.stream().map(finding -> finding.getContent()).iterator();
	}
}
