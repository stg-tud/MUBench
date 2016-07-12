package de.tu_darmstadt.stg.mubench.cli;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
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

	public DetectorOutput(DetectorArgs args) throws FileNotFoundException {
		findings = new LinkedList<>();
		findingsFile = new File(args.getFindingsFile());
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
		DumperOptions options = new DumperOptions();
		options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
		Yaml yaml = new Yaml(options);
		try (Writer writer = new OutputStreamWriter(new FileOutputStream(findingsFile), "UTF-8")) {
			yaml.dumpAll(findings.iterator(), writer);
		}
	}
}
