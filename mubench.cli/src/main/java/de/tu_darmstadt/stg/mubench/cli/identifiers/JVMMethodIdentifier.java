package de.tu_darmstadt.stg.mubench.cli.identifiers;

public class JVMMethodIdentifier implements MethodIdentifier {
    private final String originalDescriptor;
    private final String methodName;
    private final String className;
    private final String sourcePath;

    public JVMMethodIdentifier(String descriptor, String methodName, String className, String sourcePath) {
        this.originalDescriptor = descriptor;
        this.methodName = methodName;
        this.className = className;
        this.sourcePath = sourcePath;
    }

    @Override
    public String getSignature() {
        return methodName + String.format("(%s)", new JVMMethodFormatConverter().convert(originalDescriptor));
    }

    @Override
    public String getSourceFilePath() {
        return sourcePath;
    }

    public String getDeclaringTypeName() {
        return className;
    }
}
