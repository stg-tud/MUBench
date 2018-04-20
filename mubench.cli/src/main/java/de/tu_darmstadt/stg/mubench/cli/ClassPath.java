package de.tu_darmstadt.stg.mubench.cli;

/**
 * Represents a Java classpath.
 */
public class ClassPath {
    private final String path;

    /**
     * @param path a string representation of a classpath. Individual entries should be separated by colon (':').
     */
    @SuppressWarnings("WeakerAccess")
    public ClassPath(String path) {
        this.path = path;
    }

    /**
     * @return the individual classpath entries in this classpath
     */
    public String[] getPaths() {
        if (path != null && !path.isEmpty()) {
            return path.split(":");
        } else {
            return new String[0];
        }
    }

    /**
     * @return a string representation of this classpath
     */
    public String getClasspath() {
        return path;
    }

    /**
     * @param other another classpath to append to this classpath
     * @return a <b>new</b> {@link ClassPath} instance that combines this classpath and one passed as an argument
     */
    public ClassPath join(ClassPath other){
        if (other.getClasspath() == null || other.getClasspath().isEmpty()) {
            return new ClassPath(path);
        }

        if (path == null || path.isEmpty()) {
            return new ClassPath(other.getClasspath());
        }

        return new ClassPath(path + ":" + other.getClasspath());
    }

    /**
     * @param entry a classpath entry to append to this classpath
     * @return a <b>new</b> {@link ClassPath} instance that combines this classpath and the passed classpath entry
     */
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
