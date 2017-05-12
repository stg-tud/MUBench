package de.tu_darmstadt.stg.mubench.cli;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

import de.tu_darmstadt.stg.yaml.YamlCollection;
import de.tu_darmstadt.stg.yaml.YamlObject;

public class DetectorOutput {
    private final YamlCollection findings = new YamlCollection();
    private final YamlObject runInfo;

    static Builder create() {
        return new Builder();
    }

    DetectorOutput(YamlObject runInfo, List<DetectorFinding> findings) {
        this.runInfo = runInfo;
        this.findings.appendDocuments(findings);
    }

    YamlCollection getFindings() {
        return findings;
    }

    YamlObject getRunInfo() {
        return runInfo;
    }

    @SuppressWarnings({"WeakerAccess", "SameParameterValue", "unused"})
    public static class Builder {
        private YamlObject runInfo = new YamlObject();

        public Builder withRunInfo(String key, String value) {
            runInfo.put(key, value);
            return this;
        }

        public Builder withRunInfo(String key, Number value) {
            runInfo.put(key, value);
            return this;
        }

        public Builder withRunInfo(String key, Iterable<String> value) {
            runInfo.put(key, value);
            return this;
        }

        public Builder withRunInfo(String key, YamlObject value) {
            runInfo.put(key, value);
            return this;
        }

        public DetectorOutput andWithFindings(List<DetectorFinding> violations) {
            return new DetectorOutput(runInfo, violations);
        }

        public <V> DetectorOutput andWithFindings(List<V> violations, Function<V, DetectorFinding> mapper) {
            return andWithFindings(violations.stream().map(mapper).collect(Collectors.toList()));
        }
    }
}
