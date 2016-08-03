package de.tu_darmstadt.stg.mubench.utils;

import static org.junit.Assert.assertEquals;

import java.io.ByteArrayInputStream;

import org.junit.Test;

import com.github.javaparser.ParseException;

public class MethodExtractorTest {

	@Test
	public void findsMethodByName() throws ParseException {
		testFindsMethod("class C {\n"
				+ "  public void m() {\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"// declaring class: C\n"
				+ "public void m() {\n}");
	}
	
	@Test
	public void findsMethodBySignature() throws ParseException {
		testFindsMethod("class C{\n"
				+ "  void m(int i) {}\n"
				+ "  void m(Object o) {}\n"
				+ "}",
				
				"m(int)",
				
				"// declaring class: C\n"
				+ "void m(int i) {\n}");
	}
	
	@Test
	public void findsMethodBySignatureSimpleTypeName() throws ParseException {
		testFindsMethod("class C{\n"
				+ "  void m(java.lang.List l) {}\n"
				+ "  void m(Object o) {}\n"
				+ "}",
				
				"m(List)",
				
				"// declaring class: C\n"
				+ "void m(java.lang.List l) {\n}");
	}
	
	@Test
	public void findsMethodByMultipleParameterSignature() throws ParseException {
		testFindsMethod("class C{\n"
				+ "  void m(A a, B b) {}\n"
				+ "}",
				
				"m(A, B)",
				
				"// declaring class: C\n"
				+ "void m(A a, B b) {\n}");
	}
	
	@Test
	public void findsConstructor() throws ParseException {
		testFindsMethod("class C{\n"
				+ "  C() {}\n"
				+ "}",
				
				"<init>()",
				
				"// declaring class: C\n"
				+ "C() {\n}");
	}

	@Test
	public void includesBody() throws ParseException {
		testFindsMethod("class C {\n"
				+ "  public void m() {\n"
				+ "    if (true) {\n"
				+ "      m();\n"
				+ "    }\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"// declaring class: C\n"
				+ "public void m() {\n"
				+ "    if (true) {\n"
				+ "        m();\n"
				+ "    }\n"
				+ "}");
	}

	@Test
	public void includesComment() throws ParseException {
		testFindsMethod("class C {\n"
				+ "  /* comment */\n"
				+ "  public void m() {\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"/* comment */\n"
				+ "// declaring class: C\n"
				+ "public void m() {\n"
				+ "}");
	}

	@Test
	public void includesJavaDocComment() throws ParseException {
		testFindsMethod("class C {\n"
				+ "  /**\n"
				+ "   * comment\n"
				+ "   */\n"
				+ "  public void m() {\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"/**\n"
				+ "   * comment\n"
				+ "   */\n"
				+ "// declaring class: C\n"
				+ "public void m() {\n"
				+ "}");
	}
	
	@Test
	public void returnsLineNumber() throws ParseException {
		String output = runUUT("class C {\n"
				+ "  void m() {}\n"
				+ "}",
				
				"m()");
		String line_number = output.split(":")[0];
		assertEquals("2", line_number);
	}
	
	@Test
	public void returnsAllCandidates() throws ParseException {
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

	public void testFindsMethod(String input, String methodSignature, String expectedOutput) throws ParseException {
		String output = runUUT(input, methodSignature);
		String method_code = output.split(":", 2)[1];
		assertEquals(expectedOutput, method_code);
	}

	public String runUUT(String input, String methodSignature) throws ParseException {
		MethodExtractor methodExtractor = new MethodExtractor();
		ByteArrayInputStream inputStream = new ByteArrayInputStream(input.getBytes());
		return methodExtractor.extract(inputStream, methodSignature);
	}
}
