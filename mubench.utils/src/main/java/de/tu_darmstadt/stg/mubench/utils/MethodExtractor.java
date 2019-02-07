package de.tu_darmstadt.stg.mubench.utils;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.google.common.base.Joiner;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

import static com.github.javaparser.ParseStart.COMPILATION_UNIT;
import static com.github.javaparser.Providers.provider;

public class MethodExtractor {
	public static void main(String[] args) throws IOException {
		String fileName = args[0];
		String methodSignature = args[1];

		System.out.println(new MethodExtractor().extract(new FileInputStream(fileName), methodSignature));
	}

	public String extract(InputStream codeStream, String methodSignature) throws IOException {
		List<String> codeLines = readLines(codeStream);
		List<MethodCodeFragment> methods = findMethods(methodSignature, codeLines);
		
		List<String> output = new ArrayList<>();
		for (MethodCodeFragment fragment : methods) {
			output.add(fragment.asString(codeLines));
		}
		
		return Joiner.on("\n===\n").join(output);
	}

	private List<String> readLines(InputStream codeStream) throws IOException {
		List<String> lines = new ArrayList<>();
		try (BufferedReader reader = new BufferedReader(new InputStreamReader(codeStream))) {
			for (String line; (line = reader.readLine()) != null;) {
				lines.add(line);
			}
		}
		return lines;
	}

	private List<MethodCodeFragment> findMethods(String methodSignature, List<String> codeLines) {
		List<MethodCodeFragment> methods = new ArrayList<>();
		JavaParser javaParser = new JavaParser(new ParserConfiguration().setLanguageLevel(ParserConfiguration.LanguageLevel.RAW));
		ParseResult<CompilationUnit> parseResult = javaParser.parse(COMPILATION_UNIT, provider(toStream(codeLines)));
		CompilationUnit cu = parseResult.getResult().get();
		new MethodRetriever(methodSignature, false).visit(cu, methods);
		if (methods.isEmpty())
			new MethodRetriever(methodSignature, true).visit(cu, methods);
		return methods;
	}
	
	private InputStream toStream(List<String> lines) {
		return new ByteArrayInputStream(StringUtils.toString(lines).getBytes());
	}

	static class MethodCodeFragment {
		protected int firstLineNumber;
		protected int lastLineNumber;
		protected String declaringTypeName;
		
		public String asString(List<String> codeLines) {
			codeLines = codeLines.subList(firstLineNumber - 1, lastLineNumber);
			return firstLineNumber + ":" + declaringTypeName + ":" + StringUtils.toString(codeLines);
		}
	}

	static class DefaultConstructorFragment extends MethodCodeFragment {
		@Override
		public String asString(List<String> codeLines) {
			return firstLineNumber + ":" + declaringTypeName + ":" + declaringTypeName +
					"() { /* compiler-generated default constructor -- may contain field initialization code */ }";
		}
	}
}
