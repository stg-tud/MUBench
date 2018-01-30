package de.tu_darmstadt.stg.mubench.cli;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class ClassPathTest {
    @Test
    public void getClasspath(){
        ClassPath uut = new ClassPath("-path-");
        assertEquals("-path-", uut.getClasspath());
    }

    @Test
    public void getPathsSplitsPath() {
        ClassPath uut = new ClassPath("-path-:-other-path-");
        assertArrayEquals(new String[]{"-path-", "-other-path-"}, uut.getPaths());
    }
}
