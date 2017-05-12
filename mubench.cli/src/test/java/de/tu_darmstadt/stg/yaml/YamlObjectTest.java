package de.tu_darmstadt.stg.yaml;

import org.hamcrest.Matcher;
import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.collection.IsMapContaining.hasEntry;
import static org.junit.Assert.assertThat;

public class YamlObjectTest {
    @Test
    public void storesString() throws Exception {
        YamlObject object = new YamlObject();

        object.put(":key:", ":value:");

        assertThat(object.getContent(), hasEntry(":key:", ":value:"));
    }

    @Test
    public void storesNumber() throws Exception {
        YamlObject object = new YamlObject();

        object.put(":key:", 5);

        assertThat(object.getContent(), hasEntry(":key:", 5));
    }

    @Test
    public void storesIterable() throws Exception {
        YamlObject object = new YamlObject();

        object.put(":key:", Arrays.asList(":a:", ":b:", ":c:"));

        //noinspection unchecked
        assertThat(object.getContent(), (Matcher) hasEntry(is(":key:"), contains(":a:", ":b:", ":c:")));
    }

    @Test
    public void storesYamlObject() throws Exception {
        YamlObject object = new YamlObject();

        object.put(":key:", new YamlObject() {{
            put(":key2:", ":value:");
        }});

        //noinspection unchecked
        assertThat(object.getContent(), (Matcher) hasEntry(is(":key:"), hasEntry(":key2:", ":value:")));
    }

    /**
     * SnakeYaml gets confused by Carriage Return.
     */
    @Test
    public void removesCarriageReturn() throws Exception {
        YamlObject object = new YamlObject();

        object.put(":key1:", ":val\r\nue:");
        object.put(":key2:", Collections.singletonList(":val\r\nue:"));

        //noinspection unchecked
        assertThat(object.getContent(), allOf(
                hasEntry(":key1:", ":val\nue:"),
                (Matcher) hasEntry(is(":key2:"), contains(":val\nue:"))
        ));
    }
}