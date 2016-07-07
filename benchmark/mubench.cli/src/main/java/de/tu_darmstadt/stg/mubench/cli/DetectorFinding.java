package de.tu_darmstadt.stg.mubench.cli;

import java.util.HashMap;
import java.util.Map;

public class DetectorFinding {
	private static final String keyFile = "file";
	private static final String keyMethod = "method";

	private final HashMap<String, String> content;

	public DetectorFinding(String file, String method) {
		content = new HashMap<>();
		if (file != null) {
			content.put(keyFile, file);
		}
		if (method != null) {
			content.put(keyMethod, method);
		}
	}

	public String put(String key, String value) {
		return content.put(key, value);
	}

	public Map<String, String> getContent() {
		return content;
	}
}
