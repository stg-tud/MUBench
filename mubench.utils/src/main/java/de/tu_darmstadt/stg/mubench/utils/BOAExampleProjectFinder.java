package de.tu_darmstadt.stg.mubench.utils;

import edu.iastate.cs.boa.*;

import java.util.Arrays;
import java.util.Optional;

public class BOAExampleProjectFinder {
    private final BoaClient client;

    public static void main(String[] args) throws BoaException {
        String username = args[0];
        String password = args[1];
        String[] targetTypes = args[2].split(":");

        System.out.println("Logging in...");
        BOAExampleProjectFinder exampleFinder = new BOAExampleProjectFinder(username, password);
        System.out.println("Searching example projects for " + Arrays.toString(targetTypes) + "...");
        JobHandle jobHandle = exampleFinder.findExampleProjects(targetTypes);

        if (isSuccessful(jobHandle)) {
            if (hasOutput(jobHandle)) {
                System.out.println("Start output:");
                System.out.println(fetchOutput(jobHandle));
                System.out.println("===");
            } else {
                System.out.println("No output (empty).");
            }
        } else {
            System.out.println("No output (error)!");
        }
    }

    private BOAExampleProjectFinder(String username, String password) throws LoginException {
        client = new BoaClient();
        client.login(username, password);
    }

    private JobHandle findExampleProjects(String[] types) throws BoaException {
        String query = createQuery(types);
        Optional<JobHandle> job = findExistingJob(query);
        JobHandle jobHandle;
        if (job.isPresent()) {
            System.out.print("Found existing job...");
            jobHandle = job.get();
        } else {
            System.out.print("Starting new query...");
            jobHandle = startNewJob(query);
        }
        waitForJobToFinish(jobHandle);
        return jobHandle;
    }

    private static String createQuery(String[] targetTypes) {
        StringBuilder query = new StringBuilder("p: Project = input;\n")
                .append("out: output set of string;\n")
                .append("\n")
                .append("projects: set of string;\n")
                .append("files: set of string;\n");

        for (String targetType : targetTypes) {
            query.append("imports_").append(getSimpleName(targetType)).append(": bool;\n");
            query.append("uses_").append(getSimpleName(targetType)).append(": bool;\n");
        }

        query.append("\n")
                .append("visit(p, visitor {\n")
                .append("    before repo: CodeRepository -> {\n")
                .append("        # Visit only newest snapshot.\n")
                .append("        snapshot := getsnapshot(repo, \"SOURCE_JAVA_JLS\");\n")
                .append("        foreach (i: int; def(snapshot[i])) {\n")
                .append("            visit(snapshot[i]);\n")
                .append("        }\n")
                .append("        stop;\n")
                .append("    }\n")
                .append("    before f: ChangedFile -> {\n")
                .append("        if (contains(projects, p.name) || contains(files, f.name) || match(\"test\", lowercase(f.name))) stop;\n")
                .append("        add(files, f.name);\n")
                .append("    }\n")
                .append("    before astRoot: ASTRoot -> {\n")
                .append("        imports: = astRoot.imports;\n");

        for (String targetType : targetTypes) {
            query.append("        imports_").append(getSimpleName(targetType)).append(" = false;\n");
        }

        query.append("        # Check imports to know whether simple type references match the type.\n")
                .append("        # `java.lang.*` types are always implicitly imported.\n")
                .append("        foreach (i: int; def(imports[i])) {\n");

        for (String targetType : targetTypes) {
            if (getPackageStarName(targetType).equals("java.lang.*")) {
                // java.lang.* is always imported
                query.append("            imports_").append(getSimpleName(targetType)).append(" = true;\n");
            } else {
                query.append("            if ((imports[i] == \"").append(targetType).append("\") || (imports[i] == \"").append(getPackageStarName(targetType)).append("\")) {\n")
                        .append("                imports_").append(getSimpleName(targetType)).append(" = true;\n")
                        .append("            }\n");
            }
        }

        query.append("        }\n")
                .append("    }\n")
                .append("    before method: Method -> {\n")
                .append("        if (contains(projects, p.name)) stop;\n")

        for (String targetType : targetTypes) {
            query.append("        uses_").append(getSimpleName(targetType)).append(" = false;\n");
        }

        query.append("    }\n")
                .append("    before variable: Variable -> {\n");

        for (String targetType : targetTypes) {
            query.append("        if ((imports_").append(getSimpleName(targetType)).append(" && ")
                    .append("(variable.variable_type.name == \"").append(getSimpleName(targetType)).append("\")) || \n")
                    .append("            (variable.variable_type.name == \"").append(targetType).append("\")) {\n")
                    .append("            uses_").append(getSimpleName(targetType)).append(" = true;\n")
                    .append("        }\n");
        }

        query.append("    }\n")
                .append("    after method: Method -> {\n")
                .append("        if (");

        for (int i = 0; i < targetTypes.length; i++) {
            if (i > 0) {
                query.append(" && ");
            }
            query.append("uses_").append(getSimpleName(targetTypes[i]));
        }

        query.append(") {\n")
                .append("            out << p.name;\n")
                .append("            add(projects, p.name);\n")
                .append("        }\n")
                .append("    }\n")
                .append("});");

        return query.toString();
    }

    private static String getSimpleName(String targetType) {
        int startIndexOfSimpleName = targetType.lastIndexOf('.') + 1;
        return targetType.substring(startIndexOfSimpleName);
    }

    private static String getPackageStarName(String targetType) {
        int startIndexOfSimpleName = targetType.lastIndexOf('.') + 1;
        return targetType.substring(0, startIndexOfSimpleName) + "*";
    }

    private Optional<JobHandle> findExistingJob(String query) throws BoaException {
        int jobCount = client.getJobCount();
        // traverse job from latest to newest, because only the first execution of a query gives an output
        for (int jobIndex = jobCount - 1; jobIndex > 0; jobIndex--) {
            try {
                JobHandle job = client.getJobList(jobIndex, 1).get(0);
                if (job.getSource().equals(query)) {
                    return Optional.of(job);
                }
            } catch (BoaException e) {
                // client failed to parse the server response...
            }
        }
        return Optional.empty();
    }

    private JobHandle startNewJob(String query) throws BoaException {
        InputHandle largeGitHubDataset = client.getDataset("2015 September/GitHub");
        return client.query(query, largeGitHubDataset);
    }

    private void waitForJobToFinish(JobHandle jobHandle) throws BoaException {
        while (isNotFinished(jobHandle)) {
            try {
                System.out.print(".");
                Thread.sleep(1000);
            } catch (InterruptedException ignored) {
            }
        }
        System.out.println(" done.");
    }

    private static boolean isNotFinished(JobHandle jobHandle) throws BoaException {
        jobHandle.refresh();
        ExecutionStatus status = jobHandle.getExecutionStatus();
        return status != ExecutionStatus.FINISHED && status != ExecutionStatus.ERROR;
    }

    private static boolean isSuccessful(JobHandle jobHandle) {
        return jobHandle.getExecutionStatus() == ExecutionStatus.FINISHED;
    }

    private static boolean hasOutput(JobHandle jobHandle) {
        try {
            return jobHandle.getOutputSize() > 0;
        } catch (BoaException e) {
            // BOA seems to throw "not authenticated", when the output is empty. Since we know we are authenticated at
            // this point (otherwise, we wouldn't have been able to place the query in the first place), I think we can
            // safely ignore this and assume that there is no output.
            return false;
        }
    }

    private static String fetchOutput(JobHandle jobHandle) {
        try {
            return jobHandle.getOutput();
        } catch (BoaException e) {
            throw new RuntimeException("This should never happen", e);
        }
    }
}
