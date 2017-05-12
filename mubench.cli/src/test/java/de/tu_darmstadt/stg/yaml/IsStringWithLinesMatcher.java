package de.tu_darmstadt.stg.yaml;

import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.hamcrest.Matcher;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.hamcrest.Matchers.arrayContaining;
import static org.hamcrest.Matchers.contains;

public class IsStringWithLinesMatcher<T> extends BaseMatcher<T> {
    private final String[] lines;

    public static Matcher<String> hasLines(String... lines) {
        return new IsStringWithLinesMatcher<String>(lines);
    }

    public static Matcher<Path> containsLines(String... lines) {
        return new IsStringWithLinesMatcher<>(lines);
    }

    private IsStringWithLinesMatcher(String... lines) {
        this.lines = lines;
    }

    @Override
    public boolean matches(Object item) {
        if (item instanceof String) {
            return arrayContaining(lines).matches(((String) item).split("\\r?\\n"));
        }
        else if (item instanceof Path) {
            try {
                return contains(lines).matches(Files.readAllLines((Path) item, Charset.forName("UTF-8")));
            } catch (IOException ignored) {}
        }
        return false;
    }

    @Override
    public void describeTo(Description description) {
        description.appendValue(lines);
    }

    @Override
    public void describeMismatch(Object item, Description description) {
        description.appendText("was ");
        if (item instanceof String) {
            description.appendValue(((String) item).split("\\r?\\n"));
        }
        else if (item instanceof Path) {
            try {
                description.appendValue(Files.readAllLines((Path) item, Charset.forName("UTF-8")));
            } catch (IOException ignored) {}
        }
    }
}
