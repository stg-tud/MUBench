package de.tu_darmstadt.stg.yaml;

import de.tu_darmstadt.stg.mubench.cli.DetectorFinding;
import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class YamlCollection implements YamlEntity {
    private final List<YamlObject> documents = new ArrayList<>();

    public void appendDocument(YamlObject document) {
        documents.add(document);
    }

    @Override
    public void write(OutputStream outputStream) throws IOException {
        try (Writer writer = new BufferedWriter(new OutputStreamWriter(outputStream, "UTF-8"))) {
            DumperOptions options = new DumperOptions();
            options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
            Yaml yaml = new Yaml(options);
            yaml.dumpAll(getContent().iterator(), writer);
        }
    }

    private List<Map<String, Object>> getContent() {
        return documents.stream().map(YamlObject::getContent).collect(Collectors.toList());
    }

    public void appendDocuments(List<? extends YamlObject> documents) {
        this.documents.addAll(documents);
    }
}
