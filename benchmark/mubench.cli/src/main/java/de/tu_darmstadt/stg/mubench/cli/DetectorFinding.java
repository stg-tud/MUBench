package de.tu_darmstadt.stg.mubench.cli;

import java.util.HashMap;

public class DetectorFinding extends HashMap<String, String> {
	private static final long serialVersionUID = 1498379638935680845L;

	private static final String keyFile = "file";
	private static final String keyMethod = "method";

	public DetectorFinding(String file, String method) {
		this.put(keyFile, file);
		this.put(keyMethod, method);
	}
}
