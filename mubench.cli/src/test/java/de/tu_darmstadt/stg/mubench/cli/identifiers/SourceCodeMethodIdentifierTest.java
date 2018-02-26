package de.tu_darmstadt.stg.mubench.cli.identifiers;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class SourceCodeMethodIdentifierTest {
    @Test
    public void keepsMuBenchNameIntact() {
        String name = "DetectorOutput(YamlObject, List)";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals(name, uut.getSignature());
    }

    @Test
    public void convertsQualifiedDetectorOutput() {
        String name = "org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl$BinaryQValue.getStream () : java.io.InputStream";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals("getStream()", uut.getSignature());
    }

    @Test
    public void separateParametersByCommaSpace() {
        String name = "DetectorOutput(YamlObject/List)";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals("DetectorOutput(YamlObject, List)", uut.getSignature());
    }

    @Test
    public void declaringTypeNameIsEmptyIfNotSpecified() {
        String name = "declaringTypeNameIsEmptyIfNotSpecified()";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals("", uut.getDeclaringTypeName());
    }

    @Test
    public void extractsDeclaringTypeName() {
        String name = "org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl$BinaryQValue.getStream () : java.io.InputStream";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals("org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl$BinaryQValue", uut.getDeclaringTypeName());
    }

    @Test
    public void extractsSimpleDeclaringTypeNameForInternalClass() {
        String name = "org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl$BinaryQValue.getStream () : java.io.InputStream";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals("BinaryQValue", uut.getSimpleDeclaringTypeName());
    }

    @Test
    public void extractsSimpleDeclaringTypeName() {
        String name = "org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl.getStream () : java.io.InputStream";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals("QValueFactoryImpl", uut.getSimpleDeclaringTypeName());
    }

    @Test
    public void extractsSourceFilePath() {
        String name = "org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl.getStream () : java.io.InputStream";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals("org/apache/jackrabbit/spi/commons/value/QValueFactoryImpl.java", uut.getSourceFilePath());
    }

    @Test
    public void extractsSourceFilePathForInternalClass() {
        String name = "org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl$BinaryQValue.getStream () : java.io.InputStream";
        SourceCodeMethodIdentifier uut = new SourceCodeMethodIdentifier(name);
        assertEquals("org/apache/jackrabbit/spi/commons/value/QValueFactoryImpl.java", uut.getSourceFilePath());
    }
}
