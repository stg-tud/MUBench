package de.tu_darmstadt.stg.mubench.utils;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.type.TypeParameter;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.google.common.base.Joiner;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Stack;

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
		new MethodRetriever(methodSignature).visit(cu, methods);
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

	private static class MethodRetriever extends VoidVisitorAdapter<List<MethodCodeFragment>> {
		private static final String ctorId = ".ctor";

		private static final String bytecodeStaticInitializerId = "<clinit>()";
		private static final String sourcecodeStaticInitializerId = "static()";

		private String methodSignature;
		private Stack<String> currentEnclosingType;
		private List<TypeParameter> typeParameters;

		MethodRetriever(String methodSignature) {
			this.methodSignature = normalize(methodSignature);
			this.currentEnclosingType = new Stack<>();
			this.typeParameters = new ArrayList<>();
		}

		private static String normalize(String methodSignature) {
		    if (methodSignature.equals(MethodRetriever.bytecodeStaticInitializerId) ||
					methodSignature.equals(MethodRetriever.sourcecodeStaticInitializerId)) {
		    	return methodSignature;
			}
			return removeGenericTypeParameters(removeOuterTypeQualifiers(methodSignature));
		}

		private static String removeGenericTypeParameters(String methodSignature) {
			if (methodSignature.startsWith("<init>")) {
				methodSignature = ctorId + methodSignature.substring(6);
			}
			return methodSignature.replaceAll("<[^>]+>", "");
		}

		private static String removeOuterTypeQualifiers(String methodSignature) {
			return methodSignature.replaceAll("[^ (]+\\$", "");
		}

		@Override
		public void visit(ClassOrInterfaceDeclaration type, List<MethodCodeFragment> matchingMethodsCode) {
			currentEnclosingType.push(type.getName().asString());
			super.visit(type, matchingMethodsCode);

			if (methodSignature.equals(MethodRetriever.ctorId + "()") && matchingMethodsCode.isEmpty()) {
				MethodCodeFragment defaultConstructorFragment = new DefaultConstructorFragment();
				defaultConstructorFragment.declaringTypeName = type.getName().asString();
				defaultConstructorFragment.firstLineNumber = type.getBegin().get().line;
				defaultConstructorFragment.lastLineNumber = defaultConstructorFragment.firstLineNumber;
				matchingMethodsCode.add(defaultConstructorFragment);
			}

			currentEnclosingType.pop();
		}
		
		@Override
		public void visit(ConstructorDeclaration constructor, List<MethodCodeFragment> matchingMethodsCode) {
			String name = constructor.getName().asString();
			List<Parameter> parameters = constructor.getParameters();

			int typeNestingDepth = currentEnclosingType.size();
			do {
				String signature = getSignature(ctorId, parameters);
				String altSignature = getSignature(name, parameters);

				if (methodSignature.equals(signature) || methodSignature.equals(altSignature)) {
					matchingMethodsCode.add(getCode(constructor));
					return; // stop when we have a match
				}

				// if the query method signature was extracted from bytecode and the target constructor belongs to a
				// non-static inner class, then the constructor has additional parameters of the surrounding types'
				// types.
				if (typeNestingDepth - 2 >= 0)
					parameters.add(0, new Parameter(new ClassOrInterfaceType(currentEnclosingType.get(typeNestingDepth - 2)), " "));

				typeNestingDepth--;
			} while (typeNestingDepth >= 0);

			super.visit(constructor, matchingMethodsCode);
		}

		@Override
		public void visit(MethodDeclaration method, List<MethodCodeFragment> matchingMethodsCode) {
			String signature = getSignature(method.getName().asString(), method.getParameters());
			if (methodSignature.equals(signature)) {
				matchingMethodsCode.add(getCode(method));
			}
			super.visit(method, matchingMethodsCode);
		}

		@Override
		public void visit(InitializerDeclaration initializer, List<MethodCodeFragment> matchingMethodsCode) {
			if (methodSignature.equals(MethodRetriever.bytecodeStaticInitializerId) || methodSignature.equals(MethodRetriever.sourcecodeStaticInitializerId)
					&& initializer.isStatic()) {
				matchingMethodsCode.add(getCode(initializer));
			}
			super.visit(initializer, matchingMethodsCode);
		}

		@Override
		public void visit(TypeParameter typeParameter, List<MethodCodeFragment> matchingMethodsCode) {
			typeParameters.add(typeParameter);
			super.visit(typeParameter, matchingMethodsCode);
		}
		
		private <T extends Node> MethodCodeFragment getCode(T node) {
			MethodCodeFragment fragment = new MethodCodeFragment();
			fragment.declaringTypeName = getEnclosingTypeName();
			if (node.getComment().isPresent()) {
				fragment.firstLineNumber = node.getComment().get().getRange().get().begin.line;
			} else {
				fragment.firstLineNumber = node.getRange().get().begin.line;
			}
			fragment.lastLineNumber = node.getRange().get().end.line;
			return fragment;
		}
		
		private String getEnclosingTypeName() {
			return Joiner.on(".").join(currentEnclosingType);
		}

		private String getSignature(String methodName, List<Parameter> parameters) {
			StringBuilder signature = new StringBuilder(methodName).append("(");
			boolean first = true;
			for (Parameter parameter : parameters) {
				if (!first) {
					signature.append(", ");
				}
				String typeName = parameter.getType().toString();
				int endOfQualifier = typeName.lastIndexOf('.');
				if (endOfQualifier > -1) {
					typeName = typeName.substring(endOfQualifier + 1);
				}
				int startOfTypeParameters = typeName.indexOf('<');
				int endOfTypeParameters = typeName.lastIndexOf('>');
				if (startOfTypeParameters > -1 && endOfTypeParameters > -1) {
					typeName = typeName.substring(0, startOfTypeParameters) + typeName.substring(endOfTypeParameters + 1, typeName.length());
				}
				for (TypeParameter typeParameter : typeParameters) {
					String typeParameterName = typeParameter.getName().asString();
					if (typeName.contains(typeParameterName)) {
						typeName = typeName.replaceFirst(typeParameterName, "Object");
					}
				}
				signature.append(typeName);
				// if a parameter is declared like m(int foo[]), the parser drops the array brackets
				if (parameter.toString().endsWith("]")) {
					String arrayBrackets = parameter.toString().substring(parameter.toString().indexOf('['));
					signature.append(arrayBrackets);
				}
				if (parameter.isVarArgs()) {
					signature.append("[]");
				}
				first = false;
			}
			return signature.append(")").toString();
		}
	}
}
