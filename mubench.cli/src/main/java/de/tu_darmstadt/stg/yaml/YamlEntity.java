package de.tu_darmstadt.stg.yaml;

import java.io.IOException;
import java.io.OutputStream;

public interface YamlEntity {
    void write(OutputStream outputStream) throws IOException;
}
