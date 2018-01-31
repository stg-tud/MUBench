package de.tu_darmstadt.stg.mubench.cli;

public class ClassPath {
    private String path;

    public ClassPath(String path) {
        this.path = path;
    }

    public String[] getPaths() {
        if (path != null && !path.isEmpty()) {
            return path.split(":");
        } else {
            return new String[0];
        }
    }

    public String getClasspath() {
        return path;
    }
}
