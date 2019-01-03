package de.tu_darmstadt.stg.mubench.demo;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * A very naive detector that we use for demoing and debugging purposes. It simply reports an arbitrary file per class
 * in the target sources, plus one hard-coded true positive for a known misuse from the MUBench dataset.
 */
class DemoDetector {
    @SuppressWarnings("unused")
    public List<DemoViolation> detectViolations(String[] trainingSourcePaths, String[] targetSourcePaths)
            throws IOException {
        List<DemoViolation> violations = new ArrayList<>();

        // A read detector would be training on the trainingSourcePaths here...

        // Add one finding in a method "m()" for each Java source file in the target source paths.
        for (String targetSourcePath : targetSourcePaths) {
            violations.addAll(Files.find(Paths.get(targetSourcePath), Integer.MAX_VALUE, DemoDetector::isJavaFile)
                    .map(file -> new DemoViolation(file.toAbsolutePath().toString(), "m()"))
                    .collect(Collectors.toList()));
        }

        // Add a finding in the location of known misuse "synthetic_survey.jca.mapnull", to ensure we have at least
        // one potential hit when using the DemoDetector for debugging purposes.
        violations.add(new DemoViolation("MapNull.java", "misuse(Map)"));

        return violations;
    }

    private static boolean isJavaFile(Path p, BasicFileAttributes bfa) {
        return bfa.isRegularFile() && p.endsWith(".java");
    }
}
