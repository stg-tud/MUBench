package de.tu_darmstadt.stg.yaml;

import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;

import java.io.*;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

public class YamlObject implements YamlEntity {
    private final Map<String, Object> data = new LinkedHashMap<>();

    public void put(String key, String value) {
        data.put(key, clean(value));
    }

    public void put(String key, Number value) { data.put(key, value); }

    public void put(String key, Iterable<String> value) {
        data.put(key, clean(value));
    }

    public void put(String key, YamlObject value) {
        data.put(key, value.getContent());
    }

    private String clean(String value) {
        // SnakeYaml gets confused by CR
        value = value.replaceAll("\r", "");

        // SnakeYaml doesn't escape '=', but PyYaml cannot read it
        if (value.equals("=")) {
            value = "'" + value + "'";
        }

        return value;
    }

    private List<String> clean(Iterable<String> value) {
        return StreamSupport.stream(value.spliterator(), false).map(this::clean).collect(Collectors.toList());
    }

    Map<String, Object> getContent() {
        return data;
    }

    @Override
    public void write(OutputStream outputStream) throws IOException {
        try (Writer writer = new BufferedWriter(new OutputStreamWriter(outputStream, "UTF-8"))) {
            DumperOptions options = new DumperOptions();
            options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
            Yaml yaml = new Yaml(options);
            yaml.dump(getContent(), writer);
        }
    }
}
