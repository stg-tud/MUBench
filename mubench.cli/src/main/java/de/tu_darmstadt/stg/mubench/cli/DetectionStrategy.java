package de.tu_darmstadt.stg.mubench.cli;

import de.tu_darmstadt.stg.yaml.YamlObject;

import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

public interface DetectionStrategy {
    DetectorOutput detectViolations(DetectorArgs args) throws Exception;

    default DetectorOutput output(List<DetectorFinding> violations) {
        return new DetectorOutput(violations);
    }

    default DetectorOutput output(YamlObject runInfo, List<DetectorFinding> violations) {
        return new DetectorOutput(runInfo, violations);
    }

    default <V> List<DetectorFinding> map(List<V> violations, Function<V, DetectorFinding> mapper) {
        return violations.stream().map(mapper).collect(Collectors.toList());
    }
}
