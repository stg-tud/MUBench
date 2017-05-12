package de.tu_darmstadt.stg.mubench.demo;

import de.tu_darmstadt.stg.mubench.cli.*;
import de.tu_darmstadt.stg.yaml.YamlObject;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.List;
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

            // Perform the detection on the target(s)
            Path targetSourcePath = Paths.get(args.getTargetPath().srcPath);
            List<DemoViolation> violations = detectViolations(targetSourcePath);

            long endTime = System.currentTimeMillis();

            // Collect run statistics
            YamlObject runInfo = new YamlObject() {{
                put("runtime", endTime - startTime);
            }};

            return output(runInfo, map(violations, this::toDetectorFinding));
        }

        private List<DemoViolation> detectViolations(Path targetSourcePath) throws IOException {
            return Files.find(targetSourcePath, Integer.MAX_VALUE, this::isJavaFile)
                    .map(file -> new DemoViolation(file.toAbsolutePath().toString(), "m()"))
                    .collect(Collectors.toList());
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
