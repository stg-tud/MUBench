package de.tu_darmstadt.stg.mubench.cli;

import de.tu_darmstadt.stg.yaml.YamlObject;

import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

public interface DetectionStrategy {
    DetectorOutput detectViolations(DetectorArgs args) throws Exception;

    default DetectorOutput.Builder createOutput() {
        return DetectorOutput.create();
    }
}
