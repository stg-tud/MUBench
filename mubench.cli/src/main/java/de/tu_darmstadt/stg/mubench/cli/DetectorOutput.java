package de.tu_darmstadt.stg.mubench.cli;

import java.util.*;

import de.tu_darmstadt.stg.yaml.YamlCollection;
import de.tu_darmstadt.stg.yaml.YamlObject;

@SuppressWarnings("WeakerAccess")
public class DetectorOutput {
	private final YamlCollection findings = new YamlCollection();
	private final YamlObject runInfo = new YamlObject();

    /**
     * Add a finding to the output.
     * @param file the finding's file location
     * @param method the findings's method location
     * @return the new finding
     */
	public DetectorFinding add(String file, String method) {
		DetectorFinding finding = new DetectorFinding(file, method);
		findings.appendDocument(finding);
		return finding;
	}

    YamlCollection getFindings() {
        return findings;
    }

    /**
     * Add data about the detector run to the output.
     * @param key identifier of the data
     * @param value value of the data
     */
	public void addRunInformation(String key, String value) {
		runInfo.put(key, value);
	}

    /**
     * Add data about the detector run to the output.
     * @param key identifier of the data
     * @param values values of the data
     */
	@SuppressWarnings({"unchecked", "unused"})
	public void addRunInformation(String key, Iterable<String> values) {
		runInfo.put(key, values);
	}

    YamlObject getRunInfo() {
        return runInfo;
    }
}
