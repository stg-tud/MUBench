package de.tu_darmstadt.stg.mubench.cli;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;

public class DetectorOutput {
	public static void write(File findingsFile, List<DetectorFinding> findings) throws IOException {
		DumperOptions options = new DumperOptions();
		options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
		Yaml yaml = new Yaml(options);
		yaml.dumpAll(findings.iterator(), new FileWriter(findingsFile));
	}
}
