package de.tu_darmstadt.stg.mubench.utils;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Stack;
import java.util.function.Function;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseException;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.google.common.base.Joiner;

public class MethodExtractor {
	public static void main(String[] args) throws ParseException, IOException {
		String fileName = args[0];
		String methodSignature = args[1];

		System.out.println(new MethodExtractor().extract(new FileInputStream(fileName), methodSignature));
	}

	public String extract(InputStream codeStream, String methodSignature) throws ParseException, IOException {
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

	private List<MethodCodeFragment> findMethods(String methodSignature, List<String> codeLines) throws ParseException {
		List<MethodCodeFragment> methods = new ArrayList<>();
		CompilationUnit cu = JavaParser.parse(toStream(codeLines));
		new MethodRetriever(methodSignature).visit(cu, methods);
		return methods;
	}
	
	private InputStream toStream(List<String> lines) {
		return new ByteArrayInputStream(StringUtils.toString(lines).getBytes());
	}

	static class MethodCodeFragment {
		private int firstLineNumber;
		private int lastLineNumber;
		private String declaringTypeName;
		
		public String asString(List<String> codeLines) {
			codeLines = codeLines.subList(firstLineNumber - 1, lastLineNumber);
			return firstLineNumber + ":" + declaringTypeName + ":" + StringUtils.toString(codeLines);
		}
	}

	private static class MethodRetriever extends VoidVisitorAdapter<List<MethodCodeFragment>> {
		private static final String ctorId = ".ctor";

		private String methodSignature;
		private Stack<String> currentEnclosingType;

		MethodRetriever(String methodSignature) {
			this.methodSignature = normalize(methodSignature);
			this.currentEnclosingType = new Stack<>();
		}

		private static String normalize(String methodSignature) {
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
		public void visit(ClassOrInterfaceDeclaration type, List<MethodCodeFragment> arg) {
			currentEnclosingType.push(type.getName());
			super.visit(type, arg);
			currentEnclosingType.pop();
		}
		
		@Override
		public void visit(ConstructorDeclaration constructor, List<MethodCodeFragment> matchingMethodsCode) {
			String name = constructor.getName();
			List<Parameter> parameters = constructor.getParameters();

			int typeNestingDepth = currentEnclosingType.size();
			do {
				String signature = getSignature(ctorId, parameters);
				String altSignature = getSignature(name, parameters);

				if (methodSignature.equals(signature) || methodSignature.equals(altSignature)) {
					matchingMethodsCode.add(getCode(constructor, ConstructorDeclaration::getDeclarationAsString, ConstructorDeclaration::getBlock));
					return; // stop when we have a match
				}

				// if the query method signature was extracted from bytecode and the target contstructor belongs to a
				// non-static inner class, then the constructor has additional parameters of the surrounding types'
				// types.
				if (typeNestingDepth - 2 >= 0)
					parameters.add(0, new Parameter(new ClassOrInterfaceType(currentEnclosingType.get(typeNestingDepth - 2)), new VariableDeclaratorId("")));

				typeNestingDepth--;
			} while (typeNestingDepth >= 0);

			super.visit(constructor, matchingMethodsCode);
		}

		@Override
		public void visit(MethodDeclaration method, List<MethodCodeFragment> matchingMethodsCode) {
			String signature = getSignature(method.getName(), method.getParameters());
			if (methodSignature.equals(signature)) {
				matchingMethodsCode.add(getCode(method, MethodDeclaration::getDeclarationAsString, MethodDeclaration::getBody));
			}
			super.visit(method, matchingMethodsCode);
		}
		
		private <T extends Node> MethodCodeFragment getCode(T node, Function<T, String> getDeclarationAsString, Function<T, BlockStmt> getBody) {
			MethodCodeFragment fragment = new MethodCodeFragment();
			fragment.declaringTypeName = getEnclosingTypeName();
			if (node.hasComment()) {
				fragment.firstLineNumber = node.getComment().getRange().begin.line;
			} else {
				fragment.firstLineNumber = node.getRange().begin.line;
			}
			fragment.lastLineNumber = node.getRange().end.line;
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
				if (startOfTypeParameters > -1) {
					typeName = typeName.substring(0, startOfTypeParameters);
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
