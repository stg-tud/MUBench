package de.tu_darmstadt.stg.mubench.cli;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import java.util.Collection;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;

public class DetectorOutput {
	private final File findingsFile;
	private final List<Map<String, Object>> findings;

	@Deprecated
	public DetectorOutput(DetectorArgs args) throws FileNotFoundException {
		this (args.getFindingsFile());
	}
	
	public DetectorOutput(String findingsFilePath) throws FileNotFoundException {
		findings = new LinkedList<>();
		findingsFile = new File(findingsFilePath);
	}

	public boolean add(DetectorFinding finding) {
		return findings.add(finding.getContent());
	}

	public boolean addAll(Collection<DetectorFinding> findings) {
		boolean changed = false;
		for (DetectorFinding finding : findings) {
			boolean added = add(finding);
			changed = changed || added;
		}
		return changed;
	}

	public void write() throws IOException {
		try (Writer writer = new OutputStreamWriter(new FileOutputStream(findingsFile), "UTF-8")) {
			DumperOptions options = new DumperOptions();
			options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
			Yaml yaml = new Yaml(options);
			yaml.dumpAll(findings.iterator(), writer);
		}
	}
}
