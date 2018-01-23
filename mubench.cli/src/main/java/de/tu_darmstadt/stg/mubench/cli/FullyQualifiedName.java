package de.tu_darmstadt.stg.mubench.cli;

public class FullyQualifiedName {
    private final String fqn;

    public FullyQualifiedName(String fqn) {
        this.fqn = fqn;
    }

    public String toSourceFileName() {
        return getTopLevelTypeFullyQualifiedName().replace('.', '/') + ".java";
    }

    private String getTopLevelTypeFullyQualifiedName() {
        int endOfOuterTypeName = fqn.indexOf('$');
        if (endOfOuterTypeName > -1) {
            return fqn.substring(0, endOfOuterTypeName);
        } else {
            return fqn;
        }
    }

    @Override
    public String toString() {
        return fqn;
    }
}
