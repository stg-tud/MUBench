package de.tu_darmstadt.stg.mubench.cli;

public class ClassPath {
    private String path;

    public ClassPath(String path) {
        this.path = path;
    }

    public String[] getPaths() {
        return path.split(":");
    }

    public String getClasspath() {
        return path;
    }
}
