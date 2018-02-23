package de.tu_darmstadt.stg.mubench.cli;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class MuBenchMethodNameTest {
    @Test
    public void keepsMuBenchNameIntact() {
        String name = "DetectorOutput(YamlObject, List)";
        MuBenchMethodName uut = new MuBenchMethodName(name);
        assertEquals(name, uut.getName());
    }

    @Test
    public void convertsQualifiedDetectorOutput() {
        String name = "org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl$BinaryQValue.getStream () : java.io.InputStream";
        MuBenchMethodName uut = new MuBenchMethodName(name);
        assertEquals("getStream()", uut.getName());
    }

    @Test
    public void separateParametersByCommaSpace() {
        String name = "DetectorOutput(YamlObject/List)";
        MuBenchMethodName uut = new MuBenchMethodName(name);
        assertEquals("DetectorOutput(YamlObject, List)", uut.getName());
    }

    @Test
    public void declaringTypeNameIsEmptyIfNotSpecified() {
        String name = "declaringTypeNameIsEmptyIfNotSpecified()";
        MuBenchMethodName uut = new MuBenchMethodName(name);
        assertEquals("", uut.getDeclaringTypeName());
    }

    @Test
    public void extractsDeclaringTypeName() {
        String name = "org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl$BinaryQValue.getStream () : java.io.InputStream";
        MuBenchMethodName uut = new MuBenchMethodName(name);
        assertEquals("org.apache.jackrabbit.spi.commons.value.QValueFactoryImpl$BinaryQValue", uut.getDeclaringTypeName());
    }
}
