package de.tu_darmstadt.stg.mubench.demo;

class DemoViolation {
    private final String file;
    private final String method;

    DemoViolation(String file, String method) {
        this.file = file;
        this.method = method;
    }

    public String getFile() {
        return file;
    }

    public String getMethod() {
        return method;
    }
}
