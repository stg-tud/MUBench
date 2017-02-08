package de.tu_darmstadt.stg.mubench.utils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.ByteArrayInputStream;

import org.junit.Test;

public class MethodExtractorTest {

	@Test
	public void findsMethodByName() throws Exception {
		testFindsMethod("class C {\n"
				+ "  public void m() {\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"  public void m() {\n"
				+ "  }");
	}
	
	@Test
	public void findsMethodBySignature() throws Exception {
		testFindsMethod("class C{\n"
				+ "  void m(int i) {}\n"
				+ "  void m(Object o) {}\n"
				+ "}",
				
				"m(int)",
				
				"  void m(int i) {}");
	}
	
	@Test
	public void findsMethodBySignatureSimpleTypeName() throws Exception {
		testFindsMethod("class C{\n"
				+ "  void m(java.lang.List l) {}\n"
				+ "  void m(Object o) {}\n"
				+ "}",
				
				"m(List)",
				
				"  void m(java.lang.List l) {}");
	}
	
	@Test
	public void findsMethodByMultipleParameterSignature() throws Exception {
		testFindsMethod("class C{\n"
				+ "  void m(A a, B b) {}\n"
				+ "}",
				
				"m(A, B)",
				
				"  void m(A a, B b) {}");
	}

	@Test
	public void findsMethodWithArrayParameter() throws Exception {
		testFindsMethod("class C{\n"
				+ "  void m(int[] is) {}\n"
				+ "}",

				"m(int[])",

				"  void m(int[] is) {}");
	}

	@Test
	public void findsMethodWithArrayParameterAlternativeSyntax() throws Exception {
		testFindsMethod("class C{\n"
						+ "  void m(int is[]) {}\n"
						+ "}",

				"m(int[])",

				"  void m(int is[]) {}");
	}

	@Test
	public void findsMethodWithVarArgsParameter() throws Exception {
		testFindsMethod("class C{\n"
						+ "  void m(int... is) {}\n"
						+ "}",

				"m(int[])",

				"  void m(int... is) {}");
	}

	@Test
	public void findsMethodWithGenericParameter() throws Exception {
		testFindsMethod("class C{\n"
				+ "  void m(A<B> a) {}\n"
				+ "}",
				
				"m(A)",
				
				"  void m(A<B> a) {}");
	}

    @Test
    public void findsMethodWithGenericParameter2() throws Exception {
        testFindsMethod("class C{\n"
                        + "  void m(A<B> a) {}\n"
                        + "}",

                "m(A<B>)",

                "  void m(A<B> a) {}");
    }

    @Test
    public void findsMethodWithGenericParameter3() throws Exception {
        testFindsMethod("class C{\n"
                        + "  void m(A a) {}\n"
                        + "}",

                "m(A<B>)",

                "  void m(A a) {}");
    }

	@Test
	public void findsMethodWithInnerTypeParameter() throws Exception {
		testFindsMethod("class C {\n" +
				"  class I {}\n" +
				"  void m(I i) {}\n" +
				"}",

				"m(C$I)",

				"  void m(I i) {}");
	}

	@Test
	public void findsStaticMethod() throws Exception {
		testFindsMethod("class C {\n" +
				"  static void m() {}\n" +
				"}",

				"m()",

				"  static void m() {}");
	}

	@Test
	public void findsConstructorByClassName() throws Exception {
		testFindsMethod("class C{\n"
				+ "  C() {}\n"
				+ "}",
				
				"C()",
				
				"  C() {}");
	}
	
	@Test
	public void findsConstructorByInitIdentifier() throws Exception {
		testFindsMethod("class C{\n"
				+ "  C() {}\n"
				+ "}",
				
				"<init>()",
				
				"  C() {}");
	}
	
	@Test
	public void findsMethodInInnerClass() throws Exception {
		testFindsMethod("class C {\n"
				+ "  class I {\n"
				+ "    void m() {}\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"    void m() {}");
	}
	
	@Test
	public void findsMethodInAnonymousClass() throws Exception {
		testFindsMethod("class C {\n"
				+ "  void m() {\n"
				+ "    new Object() {\n"
				+ "      void n() {}\n"
				+ "    };\n"
				+ "  }\n"
				+ "}",
				
				"n()",
				
				"      void n() {}");
	}

	@Test
	public void findsMethodInAnonymousClassInConstructor() throws Exception {
		testFindsMethod("class C {\n"
						+ "  C() {\n"
						+ "    new Object() {\n"
						+ "      void n() {}\n"
						+ "    };\n"
						+ "  }\n"
						+ "}",

				"n()",

				"      void n() {}");
	}

	@Test
	public void findsConstructorOfNonStaticInnerClass() throws Exception {
		testFindsMethod("class C {\n"
						+ "  class I {\n"
						+ "    I() {}\n"
						+ "  }\n"
						+ "}",

				"I(C)",

				"    I() {}");
	}

	@Test
	public void returnsDeclaringType() throws Exception {
		testFindsDeclaringType("class C {\n"
				+ "  void m() {}\n"
				+ "}",
				
				"m()",
				
				"C");
	}
	
	@Test
	public void returnsDeclaringTypeInInnerType() throws Exception {
		testFindsDeclaringType("class C {\n"
				+ "  class I {\n"
				+ "    void m() {}\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"C.I");
	}
	
	@Test
	public void returnsDeclaringTypeAfterInnerType() throws Exception {
		testFindsDeclaringType("class C {\n"
				+ "  class I {}\n"
				+ "  void m() {}\n"
				+ "}",
				
				"m()",
				
				"C");
	}

	@Test
	public void includesBody() throws Exception {
		testFindsMethod("class C {\n"
				+ "  public void m() {\n"
				+ "    if (true) {\n"
				+ "      m();\n"
				+ "    }\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"  public void m() {\n"
				+ "    if (true) {\n"
				+ "      m();\n"
				+ "    }\n"
				+ "  }");
	}

	@Test
	public void includesComment() throws Exception {
		testFindsMethod("class C {\n"
				+ "  /* comment */\n"
				+ "  public void m() {}\n"
				+ "}",
				
				"m()",
				
				"  /* comment */\n"
				+ "  public void m() {}");
	}

	@Test
	public void includesJavaDocComment() throws Exception {
		testFindsMethod("class C {\n"
				+ "  /**\n"
				+ "   * comment\n"
				+ "   */\n"
				+ "  public void m() {}\n"
				+ "}",
				
				"m()",
				
				"  /**\n"
				+ "   * comment\n"
				+ "   */\n"
				+ "  public void m() {}");
	}
	
	@Test
	public void returnsLineNumber() throws Exception {
		testFindsLineNumber("class C {\n"
				+ "  void m() {}\n"
				+ "}",
				
				"m()",
				
				"2");
	}
	
	@Test
	public void returnsLineNumberOfComment() throws Exception {
		testFindsLineNumber("class C {\n"
				+ "  /* comment */\n"
				+ "  void m() {}\n"
				+ "}",
				
				"m()",
				
				"2");
	}
	
	@Test
	public void returnsAllCandidates() throws Exception {
		String output = runUUT("class C {\n"
				+ "  void m(){}\n"
				+ "  class I {\n"
				+ "    void m(){}\n"
				+ "  }\n"
				+ "}",
				
				"m()");
		String[] candidates = output.split("===");
		assertEquals(2, candidates.length);
	}

	private void testFindsMethod(String input, String methodSignature, String expectedOutput) throws Exception {
		String output = runUUT(input, methodSignature);
        String[] data = output.split(":", 3);
        if (data.length < 3) {
            fail("No method found.");
        }
        String methodCode = data[2];
		assertEquals(expectedOutput, methodCode);
	}
	
	private void testFindsDeclaringType(String input, String methodSignature, String expectedDeclaringType) throws Exception {
		String output = runUUT(input, methodSignature);
		String declaringType = output.split(":", 3)[1];
		assertEquals(expectedDeclaringType, declaringType);
	}
	
	private void testFindsLineNumber(String input, String methodSignature, String expectedLineNumber) throws Exception {
		String output = runUUT(input, methodSignature);
		String lineNumber = output.split(":", 3)[0];
		assertEquals(expectedLineNumber, lineNumber);
	}

	private String runUUT(String input, String methodSignature) throws Exception {
		MethodExtractor methodExtractor = new MethodExtractor();
		ByteArrayInputStream inputStream = new ByteArrayInputStream(input.getBytes());
		return methodExtractor.extract(inputStream, methodSignature);
	}
}
