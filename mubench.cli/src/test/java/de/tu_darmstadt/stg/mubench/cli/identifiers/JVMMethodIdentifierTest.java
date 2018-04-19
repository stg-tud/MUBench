package de.tu_darmstadt.stg.mubench.cli.identifiers;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class JVMMethodIdentifierTest {
    @Test
    public void extractsSignature() {
        String descriptor = "(IDLjava/lang/Thread;)Ljava/lang/Object;";
        JVMMethodIdentifier uut = new JVMMethodIdentifier(descriptor, "m", "", "");
        assertEquals("m(int, double, Thread)", uut.getSignature());
    }

    @Test
    public void passesSourceFilePathThrough() {
        JVMMethodIdentifier uut = new JVMMethodIdentifier("", "", "", "example/path/to/File.java");
        assertEquals(uut.getSourceFilePath(), "example/path/to/File.java");
    }

    @Test
    public void passesClassNameThrough() {
        JVMMethodIdentifier uut = new JVMMethodIdentifier("", "", "C", "");
        assertEquals(uut.getDeclaringTypeName(), "C");
    }

    @Test
    public void replacesConstructorIdentifierByClassesSimpleName() {
        JVMMethodIdentifier uut = new JVMMethodIdentifier("()V;", "<init>", "java.lang.Object", "");
        assertEquals("Object()", uut.getSignature());
    }

    @Test
    public void replacesStaticConstructorIdentifierByClassesSimpleName() {
        JVMMethodIdentifier uut = new JVMMethodIdentifier("()V;", "<cinit>", "java.lang.Object", "");
        assertEquals("Object()", uut.getSignature());
    }
}
