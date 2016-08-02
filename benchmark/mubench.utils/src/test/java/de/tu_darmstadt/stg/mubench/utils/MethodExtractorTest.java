package de.tu_darmstadt.stg.mubench.utils;

import static org.junit.Assert.assertEquals;

import java.io.ByteArrayInputStream;

import org.junit.Test;

import com.github.javaparser.ParseException;

public class MethodExtractorTest {

	@Test
	public void findsMethodByName() throws ParseException {
		test("class C {\n"
				+ "  public void m() {\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"public void m() {\n}");
	}
	
	@Test
	public void findsMethodBySignature() throws ParseException {
		test("class C{\n"
				+ "  void m(int i) {}\n"
				+ "  void m(Object o) {}\n"
				+ "}",
				
				"m(int)",
				
				"void m(int i) {\n}");
	}
	
	@Test
	public void findsMethodBySignatureSimpleTypeName() throws ParseException {
		test("class C{\n"
				+ "  void m(java.lang.List l) {}\n"
				+ "  void m(Object o) {}\n"
				+ "}",
				
				"m(List)",
				
				"void m(java.lang.List l) {\n}");
	}
	
	@Test
	public void findsMethodByMultipleParameterSignature() throws ParseException {
		test("class C{\n"
				+ "  void m(A a, B b) {}\n"
				+ "}",
				
				"m(A, B)",
				
				"void m(A a, B b) {\n}");
	}
	
	@Test
	public void findsConstructor() throws ParseException {
		test("class C{\n"
				+ "  C() {}\n"
				+ "}",
				
				"<init>()",
				
				"C() {\n}");
	}

	@Test
	public void includesBody() throws ParseException {
		test("class C {\n"
				+ "  public void m() {\n"
				+ "    if (true) {\n"
				+ "      m();\n"
				+ "    }\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"public void m() {\n"
				+ "    if (true) {\n"
				+ "        m();\n"
				+ "    }\n"
				+ "}");
	}

	@Test
	public void includesComment() throws ParseException {
		test("class C {\n"
				+ "  /* comment */\n"
				+ "  public void m() {\n"
				+ "  }\n"
				+ "}",
				
				"m()",
				
				"/* comment */\n"
				+ "public void m() {\n"
				+ "}");
	}

	@Test
	public void includesJavaDocComment() throws ParseException {
		test("class C {\n"
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
				+ "public void m() {\n"
				+ "}");
	}

	public void test(String input, String methodSignature, String expectedOutput) throws ParseException {
		MethodExtractor methodExtractor = new MethodExtractor();
		ByteArrayInputStream inputStream = new ByteArrayInputStream(input.getBytes());
		String method_code = methodExtractor.extract(inputStream, methodSignature);
		assertEquals(expectedOutput, method_code);
	}
}
