package de.tu_darmstadt.stg.mubench.cli;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@SuppressWarnings("WeakerAccess")
public class DetectorFinding {
	private static final String keyId = "id";
	private static final String keyFile = "file";
	private static final String keyMethod = "method";

	private final HashMap<String, Object> content;

	/**
	 * Determines the java-file name from a fully-qualified class name.
	 * @param fqn the fully-qualified name
	 * @return the corresponding java-file name
	 */
	public static String convertFQNtoFileName(String fqn) {
		int endOfOuterTypeName = fqn.indexOf('$');
		if (endOfOuterTypeName > -1) {
			fqn = fqn.substring(0, endOfOuterTypeName);
		}
		return fqn.replace('.', '/') + ".java";
	}
	
	DetectorFinding(int id, String file, String method) {
		content = new LinkedHashMap<>();
		content.put(keyId, id);
		if (file != null) {
			content.put(keyFile, file);
		}
		if (method != null) {
			content.put(keyMethod, method);
		}
	}

	/**
	 * Add data to this finding.
	 * @param key identifier of the data
	 * @param value value of the data
	 */
	public void put(String key, String value) {
		content.put(key, clean(value));
	}

	/**
	 * Add data to this finding.
	 * @param key identifier of the data
	 * @param values values of the data
	 */
	@SuppressWarnings("unchecked")
	public void put(String key, Iterable<String> values) {
		List<String> cleanValues = new ArrayList<>();
		for (String value : values) {
			cleanValues.add(clean(value));
		}
		content.put(key, cleanValues);
	}

	private String clean(String value) {
		// SnakeYaml gets confused by CR
		value = value.replaceAll("\r", "");
		
		// SnakeYaml doesn't escape '=', but PyYaml cannot read it
		if (value.equals("=")) {
			value = "'" + value + "'";
		}
		
		return value;
	}

	Map<String, Object> getContent() {
		return content;
	}
}
