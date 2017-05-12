package de.tu_darmstadt.stg.yaml;

import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Arrays;

import static de.tu_darmstadt.stg.yaml.IsStringWithLinesMatcher.hasLines;
import static org.junit.Assert.assertThat;

public class YamlCollectionTest {
    @Test
    public void writesDocument() throws Exception {
        YamlCollection file = new YamlCollection();
        file.appendDocument(new YamlObject() {{
            put(":key1:", ":value1:");
            put(":key2:", Arrays.asList(":a:", ":b:"));
            put(":key3:", new YamlObject() {{
                put(":key4:", ":value4:");
            }});
        }});

        String content = writeToString(file);

        assertThat(content, hasLines(
                "':key1:': ':value1:'",
                "':key2:':",
                "- ':a:'",
                "- ':b:'",
                "':key3:':",
                "  ':key4:': ':value4:'"
        ));
    }

    @Test
    public void writesMultilineValue() throws Exception {
        YamlCollection file = new YamlCollection();
        file.appendDocument(new YamlObject() {{
            put(":key1:", ":line1\nline2:\n");
        }});

        String content = writeToString(file);

        assertThat(content, hasLines("':key1:': |", "  :line1", "  line2:"));
    }

    @Test
    public void writesMultiDocument() throws Exception {
        YamlCollection file = new YamlCollection();
        file.appendDocuments(Arrays.asList(
                new YamlObject() {{
                    put(":key:", ":value1:");
                }},
                new YamlObject() {{
                    put(":key:", ":value2:");
                }}));

        String content = writeToString(file);

        assertThat(content, hasLines("':key:': ':value1:'", "---", "':key:': ':value2:'"));
    }

    private String writeToString(YamlCollection file) throws IOException {
        ByteArrayOutputStream os = new ByteArrayOutputStream();
        file.write(os);
        return os.toString();
    }

}