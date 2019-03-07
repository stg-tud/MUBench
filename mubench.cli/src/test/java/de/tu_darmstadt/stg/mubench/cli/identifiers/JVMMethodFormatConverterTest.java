package de.tu_darmstadt.stg.mubench.cli.identifiers;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class JVMMethodFormatConverterTest {

    private static final String Empty = "()";
    private static final String EmptyResult = "";
    private static final String SimpleBasic = "(IZ)";
    private static final String SimpleBasicResult = "int, boolean";
    private static final String ArrayBasic = "([S[Z[C)";
    private static final String ArrayBasicResult = "short[], boolean[], char[]";
    private static final String MixBasic = "([JI[CSZ)";
    private static final String MixBasicResult = "long[], int, char[], short, boolean";
    private static final String SimpleString = "(Ljava/lang/String;)";
    private static final String SimpleStringResult = "String";
    private static final String ArrayString = "([Ljava/lang/String;[Ljava/lang/String;)";
    private static final String ArrayStringResult = "String[], String[]";
    private static final String MixString = "([Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)";
    private static final String MixStringResult = "String[], String, String[], String";
    private static final String MixBasicAndString = "(I[ZJLjava/lang/String;[S[Ljava/lang/String;)";
    private static final String MixBasicAndStringResult = "int, boolean[], long, String, short[], String[]";
    private static final String SimpleCustom = "(Lorg/test/govind/Type1;)";
    private static final String SimpleCustomResult = "Type1";
    private static final String ArrayCustom = "([Lcom/company/package/Random;[Lorg/test/govind/Type2;)";
    private static final String ArrayCustomResult = "Random[], Type2[]";
    private static final String MixBasicAndCustom = "([ILorg/test/govind/Type3;FJ[C[Ljava/lang/JavaUtil;)";
    private static final String MixBasicAndCustomResult = "int[], Type3, float, long, char[], JavaUtil[]";
    private static final String MixStringAndCustomBasic = "(Lorg/test/govind/MyObject;Ljava/lang/String;Ljava/lang/String;)";
    private static final String MixStringAndCustomBasicResult = "MyObject, String, String";
    private static final String MixStringAndCustomArray = "([Ljava/lang/String;[Lorg/findbugs/SomeType;[Ljava/lang/String;)";
    private static final String MixStringAndCustomArrayResult = "String[], SomeType[], String[]";
    private static final String MixAllBasic = "([JILorg/test/govind/ExampleType;ZB[SLjava/lang/String;Ljava/lang/String;)";
    private static final String MixAllBasicResult = "long[], int, ExampleType, boolean, byte, short[], String, String";
    private static final String MixAllArray = "([Z[Z[Lorg/test/stg/Abcd;[B[F[Lorg/test/com/Type;SS[Ljava/lang/String;)";
    private static final String MixAllArrayResult = "boolean[], boolean[], Abcd[], byte[], float[], Type[], short, short, String[]";
    private static final String SimpleCustomWithBasicCharacters = "([IJSLorg/test/govind/JSType;)";
    private static final String SimpleCustomWithBasicCharactersResult = "int[], long, short, JSType";
    private static final String ArrayCustomWithBasicCharacters = "([I[JS[Lorg/test/govind/JSType;)";
    private static final String ArrayCustomWithBasicCharactersResult = "int[], long[], short, JSType[]";

    private final JVMMethodFormatConverter extractor = new JVMMethodFormatConverter();

    /**
     * Input: ()
     * Expected: ""
     */
    @Test
    public void testEmptyParameter() {
        assertEquals(EmptyResult, extractor.convert(Empty));
    }

    /**
     * Input: (IZ)
     * Expected: int, boolean
     */
    @Test
    public void testBasicParameters() {
        assertEquals(SimpleBasicResult, extractor.convert(SimpleBasic));
    }

    /**
     * Input: ([S[Z[C)
     * Expected: short[], boolean[], char[]
     */
    @Test
    public void testArrayOfBasicParameters() {
        assertEquals(ArrayBasicResult, extractor.convert(ArrayBasic));
    }

    /**
     * Input: ([JI[CSZ)
     * Expected: long[], int, char[], short, boolean
     */
    @Test
    public void testMixOfBasicParameters() {
        assertEquals(MixBasicResult, extractor.convert(MixBasic));
    }

    /**
     * Input: (Ljava/lang/String;)
     * Expected: String
     */
    @Test
    public void testStringParameters() {
        assertEquals(SimpleStringResult, extractor.convert(SimpleString));
    }

    /**
     * Input: ([Ljava/lang/String;[Ljava/lang/String;)
     * Expected: String[], String[]
     */
    @Test
    public void testArrayOfStringParameters() {
        assertEquals(ArrayStringResult, extractor.convert(ArrayString));
    }

    /**
     * Input: ([Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)
     * Expected: String[], String, String[], String
     */
    @Test
    public void testMixOfStringParameters() {
        assertEquals(MixStringResult, extractor.convert(MixString));
    }

    /**
     * Input: (I[ZJLjava/lang/String;[S[Ljava/lang/String;)
     * Expected: int, boolean[], long, String, short[], String[]
     */
    @Test
    public void testMixOBasicAndStringParameters() {
        assertEquals(MixBasicAndStringResult, extractor.convert(MixBasicAndString));
    }

    /**
     * Input: (Lorg/test/govind/Type1;)
     * Expected: Type1
     */
    @Test
    public void testCustomParameters() {
        assertEquals(SimpleCustomResult, extractor.convert(SimpleCustom));
    }

    /**
     * Input: ([Lcom/company/package/Random;[Lorg/test/govind/Type2;)
     * Expected: Random[], Type2[]
     */
    @Test
    public void testArrayOfCustomParameters() {
        assertEquals(ArrayCustomResult, extractor.convert(ArrayCustom));
    }

    /**
     * Input: ([ILorg/test/govind/Type3;FJ[C[Ljava/lang/JavaUtil;)
     * Expected: int[], Type3, float, long, char[], JavaUtil[]
     */
    @Test
    public void testMixOBasicAndCustomParameters() {
        assertEquals(MixBasicAndCustomResult, extractor.convert(MixBasicAndCustom));
    }

    /**
     * Input: (Lorg/test/govind/MyObject;Ljava/lang/String;Ljava/lang/String;)
     * Expected: MyObject, String, String
     */
    @Test
    public void testMixOfStriAndCustomParameters() {
        assertEquals(MixStringAndCustomBasicResult, extractor.convert(MixStringAndCustomBasic));
    }

    /**
     * Input: ([Ljava/lang/String;[Lorg/findbugs/SomeType;[Ljava/lang/String;)
     * Expected: String[], SomeType[], String[]
     */
    @Test
    public void testMixOfArrayOfStriAndCustomParameters() {
        assertEquals(MixStringAndCustomArrayResult, extractor.convert(MixStringAndCustomArray));
    }

    /**
     * Input: ([JILorg/test/govind/ExampleType;ZB[SLjava/lang/String;Ljava/lang/String;)
     * Expected: long[], int, ExampleType, boolean, byte, short[], String, String
     */
    @Test
    public void testMixOfAllBasicParameters() {
        assertEquals(MixAllBasicResult, extractor.convert(MixAllBasic));
    }

    /**
     * Input: ([Z[Z[Lorg/test/stg/Abcd;[B[F[Lorg/test/com/Type;SS[Ljava/lang/String;)
     * Expected: boolean[], boolean[], Abcd[], byte[], float[], Type[], short, short, String[]
     */
    @Test
    public void testMixOfAllArrayOfParameters() {
        assertEquals(MixAllArrayResult, extractor.convert(MixAllArray));
    }


    /**
     * Input: ([IJSLorg/test/govind/JSType;)
     * Expected: int[], long, short, JSType
     */
    @Test
    public void testCustomParametersHavingBasicCharacters() {
        assertEquals(SimpleCustomWithBasicCharactersResult, extractor.convert(SimpleCustomWithBasicCharacters));
    }

    /**
     * Input: ([I[JS[Lorg/test/govind/JSType;)
     * Expected: int[], long[], short, JSType[]
     */
    @Test
    public void testArrayOfCustomParametersHavingBasicCharacters() {
        assertEquals(ArrayCustomWithBasicCharactersResult, extractor.convert(ArrayCustomWithBasicCharacters));
    }

}