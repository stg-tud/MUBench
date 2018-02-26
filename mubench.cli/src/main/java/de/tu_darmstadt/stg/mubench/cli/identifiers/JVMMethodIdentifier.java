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
        String methodName = this.methodName.equals("<init>") || this.methodName.equals("<cinit>") ? extractSimpleTypeName(this.className) : this.methodName;
        return methodName + String.format("(%s)", new JVMMethodFormatConverter().convert(originalDescriptor));
    }

    private String extractSimpleTypeName(String typeName) {
        typeName = typeName.substring(typeName.lastIndexOf(".") + 1);
        typeName = typeName.substring(typeName.lastIndexOf("/") + 1);
        typeName = typeName.substring(typeName.lastIndexOf("$") + 1);
        return typeName;
    }

    @Override
    public String getSourceFilePath() {
        return sourcePath;
    }

    public String getDeclaringTypeName() {
        return className;
    }
}
