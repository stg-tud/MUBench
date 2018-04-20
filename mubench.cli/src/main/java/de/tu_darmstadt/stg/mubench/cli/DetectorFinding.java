package de.tu_darmstadt.stg.mubench.cli;

import de.tu_darmstadt.stg.yaml.YamlObject;

/**
 * Represents one finding of a detector. A finding needs to have a file and method location, for the MUBench Pipeline
 * to correctly filter potential hits for known misuses. A finding may have additional properties, which will be
 * displayed on the MUBench Review Site during the manual reviews of the findings.
 *
 * The <i>property keys</i> will be used as column headers for displaying the findings. They may only contain characters
 * from [a-zA-Z0-9_]. The underscore will be converted to a space for display. The keys should not exceed 64 characters
 * in length, otherwise they will be cut off, which may lead to unexpected conflicts between keys.
 *
 * The <i>property values</i> may contain HTML code. As a result, HTML entities need to be properly escaped using, e.g.,
 * <code>&amp;lt;</code> for <code>&lt;</code>. Dot graphs reported in properties of a finding will automatically be
 * converted to images.
 */
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
