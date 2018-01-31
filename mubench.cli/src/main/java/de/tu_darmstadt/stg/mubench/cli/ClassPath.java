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

    public void append(ClassPath other){
        if (other.getClasspath() != null && !other.getClasspath().isEmpty()) {
            this.path += ":" + other.getClasspath();
        }
    }

    public void append(String entry) {
        if (entry != null && !entry.isEmpty()) {
            this.path += ":" + entry;
        }
    }
}
