package de.tu_darmstadt.stg.mubench.utils;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseException;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.google.common.base.Joiner;

public class MethodExtractor {
	public static void main(String[] args) throws ParseException, IOException {
		String fileName = args[0];
		String methodSignature = args[1];

		System.out.println(new MethodExtractor().extract(new FileInputStream(fileName), methodSignature));
	}

	public String extract(InputStream codeStream, String methodSignature) throws ParseException {
		CompilationUnit cu = JavaParser.parse(codeStream);

		List<String> methods = new ArrayList<>();
		new MethodRetriever(methodSignature).visit(cu, methods);

		return Joiner.on("\n\n").join(methods);
	}

	private static class MethodRetriever extends VoidVisitorAdapter<List<String>> {
		private String methodSignature;

		public MethodRetriever(String methodSignature) {
			this.methodSignature = methodSignature;
		}
		
		@Override
		public void visit(ConstructorDeclaration constructor, List<String> matchingMethodsCode) {
			String signature = getSignature("<init>", constructor.getParameters());
			if (methodSignature.equals(signature)) {
				matchingMethodsCode.add(getCode(constructor, c -> c.getDeclarationAsString(), c -> c.getBlock()));
			}
		}

		@Override
		public void visit(MethodDeclaration method, List<String> matchingMethodsCode) {
			String signature = getSignature(method.getName(), method.getParameters());
			if (methodSignature.equals(signature)) {
				matchingMethodsCode.add(getCode(method, m -> m.getDeclarationAsString(), m -> m.getBody()));
			}
		}
		
		private <T extends Node> String getCode(T node, Function<T, String> getDeclarationAsString, Function<T, BlockStmt> getBody) {
			StringBuilder method_code = new StringBuilder();
			method_code.append(node.getRange().begin.line).append(":");
			if (node.hasComment()) {
				method_code.append(node.getComment());
			}
			method_code.append(getDeclarationAsString.apply(node)).append(" ").append(getBody.apply(node));
			return method_code.toString();
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
				signature.append(typeName);
				first = false;
			}
			return signature.append(")").toString();
		}
	}
}
