package de.tu_darmstadt.stg.mubench.utils;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseException;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
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
		public void visit(MethodDeclaration method, List<String> matchingMethodsCode) {
			String signature = getSignature(method);
			if (methodSignature.equals(signature)) {
				StringBuilder method_code = new StringBuilder();
				if (method.hasComment()) {
					method_code.append(method.getComment());
				}
				method_code.append(method.getDeclarationAsString()).append(" ").append(method.getBody());
				matchingMethodsCode.add(method_code.toString());
			}
		}

		private String getSignature(MethodDeclaration method) {
			StringBuilder signature = new StringBuilder(method.getName()).append("(");
			boolean first = true;
			for (Parameter parameter : method.getParameters()) {
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
