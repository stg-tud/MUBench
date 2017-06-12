package de.tu_darmstadt.stg.mubench.utils;

import edu.iastate.cs.boa.*;

public class BOAExampleProjectFinder {
    public static void main(String[] args) throws BoaException {
        BoaClient client = new BoaClient();
        client.login(args[0], args[1]);
        System.out.println("Logged in.");
        InputHandle largeGitHubDataset = client.getDataset("2015 September/GitHub");
        System.out.println("Fetched dataset.");
        System.out.print("Running query for '" + args[2] + "'...");
        JobHandle jobHandle = client.query(createQuery(args[2]), largeGitHubDataset);
        while (isNotFinished(jobHandle)) {
            try {
                System.out.print(".");
                Thread.sleep(1000);
            } catch (InterruptedException ignored) {}
        }

        if (isSuccessful(jobHandle)) {
            System.out.println(" ok.");
            try {
                if (hasOutput(jobHandle)) {
                    System.out.println("Start output:");
                    System.out.println(jobHandle.getOutput());
                    System.out.println("===");
                } else {
                    System.out.println("No output.");
                }
            } catch (BoaException e) {
                System.out.println(String.format("No output (Exception '%s').", e.getMessage()));
            }
        } else {
            System.out.println("ERROR!");
        }
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

    private static boolean isNotFinished(JobHandle jobHandle) throws BoaException {
        jobHandle.refresh();
        ExecutionStatus status = jobHandle.getExecutionStatus();
        return status != ExecutionStatus.FINISHED && status != ExecutionStatus.ERROR;
    }

    private static boolean isSuccessful(JobHandle jobHandle) {
        return jobHandle.getExecutionStatus() == ExecutionStatus.FINISHED;
    }

    private static boolean hasOutput(JobHandle jobHandle) throws BoaException {
        try {
            return jobHandle.getOutputSize() > 0;
        } catch (BoaException e) {
            // BOA seems to throw "not authenticated", when the output is empty. Since we know we are authenticated at
            // this point (otherwise, we wouldn't have been able to place the query in the first place), I think we can
            // safely ignore this and assume that there is no output.
            return false;
        }
    }
}
