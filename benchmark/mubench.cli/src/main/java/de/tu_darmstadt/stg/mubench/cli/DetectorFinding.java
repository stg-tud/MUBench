package de.tu_darmstadt.stg.mubench.cli;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class DetectorFinding {
	private static final String keyFile = "file";
	private static final String keyMethod = "method";

	private final HashMap<String, Object> content;

	public DetectorFinding(String file, String method) {
		content = new LinkedHashMap<>();
		if (file != null) {
			content.put(keyFile, file);
		}
		if (method != null) {
			content.put(keyMethod, method);
		}
	}

	public String put(String key, String value) {
		return (String) content.put(key, clean(value));
	}
	
	@SuppressWarnings("unchecked")
	public List<String> put(String key, Collection<String> values) {
		List<String> cleanValues = new ArrayList<>();
		for (String value : values) {
			cleanValues.add(clean(value));
		}
		return (List<String>) content.put(key, cleanValues);
	}

	private String clean(String value) {
		// SnakeYaml gets confused by CR
		return value.replaceAll("\r", "");
	}

	public Map<String, Object> getContent() {
		return content;
	}
}
