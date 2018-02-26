package de.tu_darmstadt.stg.mubench.cli.identifiers;

import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SourceCodeMethodIdentifier {
    private final String parameterPattern = "\\(.*?\\)";
    private final String parameterSeparatorPattern = "([/,])";

    private final String originalName;

    public SourceCodeMethodIdentifier(String name) {
        this.originalName = name;
    }

    public String getSignature() {
        return convertToMuBenchSignature(this.originalName);
    }

    public String getSimpleDeclaringTypeName() {
        return extractSimpleDeclaringTypeName(this.originalName);
    }

    public String getSourceFilePath() {
        String declaringTypeName = extractDeclaringTypeName(this.originalName);
        String qualifiedTopLevelClassName = declaringTypeName.contains("$") ?
                declaringTypeName.substring(0, declaringTypeName.indexOf("$")) :
                declaringTypeName;
        return qualifiedTopLevelClassName.replaceAll("\\.", "/") + ".java";
    }

    private String convertToMuBenchSignature(String name) {
        String[] parameters = extractParameters(name);
        String methodName = removeParameters(name);
        methodName = removeReturnType(methodName);
        methodName = removePackageName(methodName);
        methodName = methodName.trim();
        return methodName + createParameterString(parameters);
    }

    private String extractDeclaringTypeName(String name) {
        name = removeReturnType(removeParameters(name));
        return name.contains(".") ? name.substring(0, name.lastIndexOf(".")) : "";
    }

    private String extractSimpleDeclaringTypeName(String name) {
        String declaringTypeName = extractDeclaringTypeName(name);
        return declaringTypeName.contains("$") ?
                declaringTypeName.substring(declaringTypeName.lastIndexOf("$") + 1) :
                removePackageName(declaringTypeName);
    }

    private String removeParameters(String name) {
        return name.replaceAll(parameterPattern, "");
    }

    private String[] extractParameters(String name) {
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
