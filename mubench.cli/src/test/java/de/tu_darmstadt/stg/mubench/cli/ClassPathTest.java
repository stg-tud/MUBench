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
    public void joinKeepsOriginalUnchanged() {
        ClassPath uut = new ClassPath("-path-");
        ClassPath other = new ClassPath("-other-path-");
        uut.join(other);
        assertEquals("-path-", uut.getClasspath());
    }

    @Test
    public void joinsOtherClassPath() {
        ClassPath uut = new ClassPath("-One more time-:-We're gonna celebrate-");
        ClassPath other = new ClassPath("-Oh yeah, all right-:-Don't stop the dancing-");
        String expected = "-One more time-:-We're gonna celebrate-:-Oh yeah, all right-:-Don't stop the dancing-";
        ClassPath actual = uut.join(other);
        assertEquals(expected, actual.getClasspath());
    }

    @Test
    public void joinsNothingOnEmptyPath(){
        ClassPath uut = new ClassPath("");
        ClassPath other = new ClassPath("");
        ClassPath actual = uut.join(other);
        assertEquals("", actual.getClasspath());
    }

    @Test
    public void joinsEntry() {
        ClassPath uut = new ClassPath("-We even finish each other's-");
        String entry = "-sandwiches.-";
        String expected = "-We even finish each other's-:-sandwiches.-";
        ClassPath actual = uut.join(entry);
        assertEquals(expected, actual.getClasspath());
    }

    @Test
    public void joinsNothingOnEmptyEntry(){
        ClassPath uut = new ClassPath("");
        ClassPath actual = uut.join("");
        assertEquals("", actual.getClasspath());
    }
}
