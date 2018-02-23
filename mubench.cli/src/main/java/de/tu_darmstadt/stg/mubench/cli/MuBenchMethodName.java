package de.tu_darmstadt.stg.mubench.cli;

import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MuBenchMethodName {
    private final String parameterPattern = "\\(.*?\\)";
    private final String parameterSeparatorPattern = "(/|,)";

    private final String name;
    private final String declaringTypeName;

    public MuBenchMethodName(String name) {
        this.name = convertToMuBenchName(name);
        this.declaringTypeName = getDeclaringTypeName(name);
    }

    public String getName() {
        return this.name;
    }

    public String getDeclaringTypeName() {
        return this.declaringTypeName;
    }

    private String convertToMuBenchName(String name) {
        String[] parameters = getParameters(name);
        String methodName = removeParameters(name);
        methodName = removeReturnType(methodName);
        methodName = removePackageName(methodName);
        methodName = methodName.trim();


        return methodName + createParameterString(parameters);
    }

    private String getDeclaringTypeName(String name) {
        name = removeReturnType(removeParameters(name));
        return name.contains(".") ? name.substring(0, name.lastIndexOf(".")) : "";
    }

    private String removeParameters(String name) {
        return name.replaceAll(parameterPattern, "");
    }

    private String[] getParameters(String name) {
        Matcher matcher = Pattern.compile(parameterPattern).matcher(name);
        String parameters = matcher.find() ? removeSurroundingCharacters(matcher.group(0)) : "";
        String[] splitParameters = parameters.split(parameterSeparatorPattern);
        return Arrays.stream(splitParameters).map(p -> removePackageName(p).trim()).toArray(String[]::new);
    }

    private String removePackageName(String name) {
        return name.substring(name.lastIndexOf(".") + 1);
    }

    private String removeReturnType(String name) {
        return name.split(":")[0];
    }

    private String createParameterString(String[] parameters) {
        return "(" + String.join(", ", parameters) + ")";
    }

    private String removeSurroundingCharacters(String s) {
        return s.substring(1, s.length() - 1);
    }
}
