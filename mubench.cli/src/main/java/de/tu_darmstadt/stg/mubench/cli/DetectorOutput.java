package de.tu_darmstadt.stg.mubench.cli;

import java.util.*;

import de.tu_darmstadt.stg.yaml.YamlCollection;
import de.tu_darmstadt.stg.yaml.YamlObject;

@SuppressWarnings("WeakerAccess")
public class DetectorOutput {
	private final YamlCollection findings = new YamlCollection();
	private final YamlObject runInfo;

    public DetectorOutput(List<DetectorFinding> findings) {
        this(new YamlObject(), findings);
    }

    public DetectorOutput(YamlObject runInfo, List<DetectorFinding> findings) {
        this.runInfo = runInfo;
        this.findings.appendDocuments(findings);
    }

    YamlCollection getFindings() {
        return findings;
    }

    YamlObject getRunInfo() {
        return runInfo;
    }
}
