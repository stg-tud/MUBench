package de.tu_darmstadt.stg.mubench.utils;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.type.TypeParameter;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.google.common.base.Joiner;

import java.util.ArrayList;
import java.util.List;
import java.util.Stack;

class MethodRetriever extends VoidVisitorAdapter<List<MethodExtractor.MethodCodeFragment>> {
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
    public void visit(ClassOrInterfaceDeclaration type, List<MethodExtractor.MethodCodeFragment> matchingMethodsCode) {
        currentEnclosingType.push(type.getName().asString());
        super.visit(type, matchingMethodsCode);

        if (methodSignature.equals(MethodRetriever.ctorId + "()") && matchingMethodsCode.isEmpty()) {
            MethodExtractor.MethodCodeFragment defaultConstructorFragment = new MethodExtractor.DefaultConstructorFragment();
            defaultConstructorFragment.declaringTypeName = type.getName().asString();
            defaultConstructorFragment.firstLineNumber = type.getBegin().get().line;
            defaultConstructorFragment.lastLineNumber = defaultConstructorFragment.firstLineNumber;
            matchingMethodsCode.add(defaultConstructorFragment);
        }

        currentEnclosingType.pop();
    }

    @Override
    public void visit(ConstructorDeclaration constructor, List<MethodExtractor.MethodCodeFragment> matchingMethodsCode) {
        String name = constructor.getName().asString();
        List<Parameter> parameters = constructor.getParameters();

        int typeNestingDepth = currentEnclosingType.size();
        do {
            String signature = getSignature(ctorId, parameters, typeParameters);
            String altSignature = getSignature(name, parameters, typeParameters);

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
    public void visit(MethodDeclaration method, List<MethodExtractor.MethodCodeFragment> matchingMethodsCode) {
        String signature = getSignature(method.getName().asString(), method.getParameters(), typeParameters);
        if (methodSignature.equals(signature)) {
            matchingMethodsCode.add(getCode(method));
        }
        super.visit(method, matchingMethodsCode);
    }

    @Override
    public void visit(InitializerDeclaration initializer, List<MethodExtractor.MethodCodeFragment> matchingMethodsCode) {
        if (methodSignature.equals(MethodRetriever.bytecodeStaticInitializerId) || methodSignature.equals(MethodRetriever.sourcecodeStaticInitializerId)
                && initializer.isStatic()) {
            matchingMethodsCode.add(getCode(initializer));
        }
        super.visit(initializer, matchingMethodsCode);
    }

    @Override
    public void visit(TypeParameter typeParameter, List<MethodExtractor.MethodCodeFragment> matchingMethodsCode) {
        typeParameters.add(typeParameter);
        super.visit(typeParameter, matchingMethodsCode);
    }

    private <T extends Node> MethodExtractor.MethodCodeFragment getCode(T node) {
        MethodExtractor.MethodCodeFragment fragment = new MethodExtractor.MethodCodeFragment();
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

    private static String getSignature(String methodName, List<Parameter> parameters,
                                       List<TypeParameter> typeParameters) {
        StringBuilder signature = new StringBuilder(methodName).append("(");
        boolean first = true;
        for (Parameter parameter : parameters) {
            if (!first) {
                signature.append(", ");
            }
            String typeName = parameter.getType().toString();
            typeName = stripPackageQualifier(typeName);
            typeName = stripTypeParameters(typeName);
            typeName = applyTypeErasure(typeName, typeParameters);
            signature.append(typeName);
            if (parameter.isVarArgs()) {
                signature.append("[]");
            }
            first = false;
        }
        return signature.append(")").toString();
    }

    private static String stripPackageQualifier(String typeName) {
        int endOfQualifier = typeName.lastIndexOf('.');
        if (endOfQualifier > -1) {
            typeName = typeName.substring(endOfQualifier + 1);
        }
        return typeName;
    }

    private static String stripTypeParameters(String typeName) {
        int startOfTypeParameters = typeName.indexOf('<');
        int endOfTypeParameters = typeName.lastIndexOf('>');
        if (startOfTypeParameters > -1 && endOfTypeParameters > -1) {
            typeName = typeName.substring(0, startOfTypeParameters) + typeName.substring(endOfTypeParameters + 1);
        }
        return typeName;
    }

    private static String applyTypeErasure(String typeName, List<TypeParameter> typeParameters) {
        for (TypeParameter typeParameter : typeParameters) {
            String typeParameterName = typeParameter.getName().asString();
            if (typeName.startsWith(typeParameterName)) {
                typeName = typeName.replaceFirst(typeParameterName, "Object");
            }
        }
        return typeName;
    }
}
