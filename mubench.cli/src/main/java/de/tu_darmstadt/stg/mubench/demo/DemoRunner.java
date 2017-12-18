package de.tu_darmstadt.stg.mubench.demo;

import de.tu_darmstadt.stg.mubench.cli.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class DemoRunner {
    public static void main(String[] args) throws Exception {
        new MuBenchRunner()
                .withDetectOnlyStrategy(new DemoStrategy())
                .withMineAndDetectStrategy(new DemoStrategy())
                .run(args);
    }

    private static class DemoStrategy implements DetectionStrategy {
        @Override
        public DetectorOutput detectViolations(DetectorArgs args) throws Exception {
            long startTime = System.currentTimeMillis();

            List<DemoViolation> violations = new ArrayList<>();
            for (String targetSourcePath : args.getTargetSrcPaths()) {
                violations.addAll(detectViolations(Paths.get(targetSourcePath)));
            }
            long endTime = System.currentTimeMillis();

            return createOutput()
                    .withRunInfo("runtime", endTime - startTime)
                    .withFindings(violations, this::toDetectorFinding);
        }

        private List<DemoViolation> detectViolations(Path targetSourcePath) throws IOException {
            List<DemoViolation> violations = Files.find(targetSourcePath, Integer.MAX_VALUE, this::isJavaFile)
                    .map(file -> new DemoViolation(file.toAbsolutePath().toString(), "m()"))
                    .collect(Collectors.toList());
            // Add synthetic.mapnull.mapnull to ensure we have a potential hit for debugging ex1/3
            violations.add(new DemoViolation("MapNull.java", "misuse(Map)"));
            return violations;
        }

        private DetectorFinding toDetectorFinding(DemoViolation violation) {
            return new DetectorFinding(violation.file, violation.method);
        }

        private boolean isJavaFile(Path p, BasicFileAttributes bfa) {
            return bfa.isRegularFile() && p.endsWith(".java");
        }
    }

    private static class DemoViolation {
        private final String file;
        private final String method;

        DemoViolation(String file, String method) {
            this.file = file;
            this.method = method;
        }
    }
}
