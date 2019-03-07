package de.tu_darmstadt.stg.mubench.cli;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

import de.tu_darmstadt.stg.yaml.YamlCollection;
import de.tu_darmstadt.stg.yaml.YamlObject;

/**
 * Represents the output of a detector run to the MUBench Pipeline.
 */
public class DetectorOutput {
    private final YamlCollection findings = new YamlCollection();
    private final YamlObject runInfo;

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

    /**
     * Collects detector-run output for reporting to the MUBench Pipeline.
     */
    @SuppressWarnings({"WeakerAccess", "SameParameterValue", "unused"})
    public static class Builder {
        private YamlObject runInfo = new YamlObject();

        /**
         * @param key   a key for the value to report
         * @param value the value to report
         * @return this builder, for fluent calls
         */
        public Builder withRunInfo(String key, String value) {
            runInfo.put(key, value);
            return this;
        }

        /**
         * @param key   a key for the value to report
         * @param value the value to report
         * @return this builder, for fluent calls
         */
        public Builder withRunInfo(String key, Number value) {
            runInfo.put(key, value);
            return this;
        }

        /**
         * @param key   a key for the value to report
         * @param value the value to report
         * @return this builder, for fluent calls
         */
        public Builder withRunInfo(String key, Iterable<String> value) {
            runInfo.put(key, value);
            return this;
        }

        /**
         * @param key   a key for the value to report
         * @param value the value to report
         * @return this builder, for fluent calls
         */
        public Builder withRunInfo(String key, YamlObject value) {
            runInfo.put(key, value);
            return this;
        }

        /**
         * Adding findings to the output terminates the collection of run output. The resulting object should be
         * returned from {@link DetectionStrategy#detectViolations(DetectorArgs, DetectorOutput.Builder)}.
         *
         * @param findings a list of the findings returned from the detector run. If your detector returns findings
         *                 in a representation other than {@link DetectorFinding}, you may use
         *                 {@link #withFindings(List, Function)} for conversion.
         * @return the output value object
         */
        public DetectorOutput withFindings(List<DetectorFinding> findings) {
            return new DetectorOutput(runInfo, findings);
        }


        /**
         * Adding findings to the output terminates the collection of run output. The resulting object should be
         * returned from {@link DetectionStrategy#detectViolations(DetectorArgs, DetectorOutput.Builder)}.
         *
         * @param <V> the type of findings returned by the detector.
         * @param findings a list of the findings returned from the detector run.
         * @param mapper a conversion function that turns each findings into a {@link DetectorFinding}.
         * @return the output value object
         */
        public <V> DetectorOutput withFindings(List<V> findings, Function<V, DetectorFinding> mapper) {
            return withFindings(findings.stream().map(mapper).collect(Collectors.toList()));
        }
    }
}
