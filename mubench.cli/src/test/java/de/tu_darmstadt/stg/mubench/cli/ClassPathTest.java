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

    @Test
    public void getPathsHandlesEmptyPath(){
        ClassPath uut = new ClassPath("");
        assertArrayEquals(new String[0], uut.getPaths());
    }

    @Test
    public void appendsOtherClassPath() {
        ClassPath uut = new ClassPath("-One more time-:-We're gonna celebrate-");
        ClassPath other = new ClassPath("-Oh yeah, all right-:-Don't stop the dancing-");
        String expected = "-One more time-:-We're gonna celebrate-:-Oh yeah, all right-:-Don't stop the dancing-";
        uut.append(other);
        assertEquals(expected, uut.getClasspath());
    }

    @Test
    public void appendsNothingOnEmptyPath(){
        ClassPath uut = new ClassPath("");
        ClassPath other = new ClassPath("");
        uut.append(other);
        assertEquals("", uut.getClasspath());
    }
}
