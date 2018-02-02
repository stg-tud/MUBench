package de.tu_darmstadt.stg.mubench.cli;

public class ClassPath {
    private final String path;

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

    public ClassPath join(ClassPath other){
        if (other.getClasspath() == null || other.getClasspath().isEmpty()) {
            return new ClassPath(path);
        }

        if (path == null || path.isEmpty()) {
            return new ClassPath(other.getClasspath());
        }

        return new ClassPath(path + ":" + other.getClasspath());
    }

    public ClassPath join(String entry) {
        if (entry == null || entry.isEmpty()) {
            return new ClassPath(path);
        }

        if (path == null || path.isEmpty()) {
            return new ClassPath(entry);
        }

        return new ClassPath(path + ":" + entry);
    }
}
