package de.tu_darmstadt.stg.mubench.utils;

import edu.iastate.cs.boa.*;

import java.util.Optional;

public class BOAExampleProjectFinder {
    private final BoaClient client;

    public static void main(String[] args) throws BoaException {
        String username = args[0];
        String password = args[1];
        String targetType = args[2];

        System.out.println("Logging in...");
        BOAExampleProjectFinder exampleFinder = new BOAExampleProjectFinder(username, password);
        System.out.println("Searching example projects for " + targetType + "...");
        JobHandle jobHandle = exampleFinder.findExampleProjects(targetType);

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

    private JobHandle findExampleProjects(String type) throws BoaException {
        String query = createQuery(type);
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

    private static String createQuery(String targetType) {
        int startIndexOfSimpleName = targetType.lastIndexOf('.') + 1;
        String packageStarName = targetType.substring(0, startIndexOfSimpleName) + "*";
        String simpleTypeName = targetType.substring(startIndexOfSimpleName);
        return "p: Project = input;\n" +
                "out: output set of string;\n" +
                "\n" +
                "files: set of string;\n" +
                "revision: Revision;\n" +
                "file: ChangedFile;\n" +
                "imports_package: bool;\n" +
                "\n" +
                "visit(p, visitor {\n" +
                "    before r: Revision -> revision = r;\n" +
                "    before f: ChangedFile -> {\n" +
                "        if (contains(files, f.name) || match(\"test\", lowercase(f.name))) stop;\n" +
                "        file = f;\n" +
                "    }\n" +
                "    after f: ChangedFile -> add(files, f.name);\n" +
                "    before astRoot: ASTRoot -> {\n" +
                "        imports: = astRoot.imports;\n" +
                "        imports_package = false;\n" +
                "        foreach (i: int; def(imports[i])) {\n" +
                "            if (imports[i] == \"" + targetType + "\") {\n" +
                "                out << p.name;\n" +
                "                stop;\n" +
                "            } else if (imports[i] == \"" + packageStarName + "\") {\n" +
                "                imports_package = true;\n" +
                "                break;\n" +
                "            }\n" +
                "        }\n" +
                "    }\n" +
                "    before variable: Variable -> {\n" +
                "        if ((imports_package && (variable.variable_type.name == \"" + simpleTypeName + "\")) || \n" +
                "            (variable.variable_type.name == \"" + targetType + "\")) {\n" +
                "            out << p.name;\n" +
                "            stop;\n" +
                "        }\n" +
                "    }\n" +
                "});";
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
