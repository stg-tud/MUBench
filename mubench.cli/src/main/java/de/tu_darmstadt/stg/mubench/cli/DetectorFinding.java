package de.tu_darmstadt.stg.mubench.cli;

import de.tu_darmstadt.stg.yaml.YamlObject;

@SuppressWarnings("WeakerAccess")
public class DetectorFinding extends YamlObject {
	private static final String keyFile = "file";
	private static final String keyMethod = "method";

	public DetectorFinding(String file, String method) {
		if (file != null) {
			put(keyFile, file);
		}
		if (method != null) {
			put(keyMethod, method);
		}
	}
}
