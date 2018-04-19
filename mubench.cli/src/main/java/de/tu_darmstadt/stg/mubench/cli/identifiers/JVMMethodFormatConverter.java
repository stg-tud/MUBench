package de.tu_darmstadt.stg.mubench.cli.identifiers;

import java.util.Map;
import java.util.Map.Entry;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This class converts from JVM method representation to the method representation in MUBench
 *
 * @author govind singh, mattis manfred kaemmerer
 */
public class JVMMethodFormatConverter {
    /* Constants */
    private static final char TYPEBYTEASCHAR = 'B';
    private static final String TYPEBYTEASSTRING = "byte";
    private static final char TYPECHARACTERASCHAR = 'C';
    private static final String TYPECHARACTERASSTRING = "char";
    private static final char TYPEDOUBLEASCHAR = 'D';
    private static final String TYPEDOUBLEASSTRING = "double";
    private static final char TYPEFLOATASCHAR = 'F';
    private static final String TYPEFLOATASSTRING = "float";
    private static final char TYPELONGASCHAR = 'J';
    private static final String TYPELONGASSTRING = "long";
    private static final char TYPEINTASCHAR = 'I';
    private static final String TYPEINTASSTRING = "int";
    private static final char TYPESHORTASCHAR = 'S';
    private static final String TYPESHORTASSTRING = "short";
    private static final char TYPEBOOLEANASCHAR = 'Z';
    private static final String TYPEBOOLEANASSTRING = "boolean";

    /**
     * Pattern for Primitive types.
     * B->byte, C->char, D->double, F->float, I->int, J->long, S->short, Z->boolean
     * Since even the parameter name can begin with any of this reserved alphabet when
     * parameter is a custom class, the immediate next alphabet being a lowercase letter
     * differentiate it from these basic types.
     */
    private static final String BASICTYPEPATTERN = "(?<!\\[)[BCDFIJSZ](?![a-z])";
    /**
     * pattern is [B for byte array, [C for char array etc.
     */
    private static final String BASICTYPEARRAYPATTERN = "\\[[BCDFIJSZ](?![a-z])";
    /**
     * pattern is Ljava/lang/String
     */
    private static final String STRINGPATTERN = ".*(?<!\\[)Ljava/lang/String$";
    /**
     * pattern is [Ljava/lang/String
     */
    private static final String STRINGARRAYPATTERN = ".*\\[Ljava/lang/String$";
    /**
     * pattern is Lcom/company/package/Type
     */
    private static final String CUSTOMTYPEPATTERN = ".*(?<!\\[)L.*(?<!String)$";
    /**
     * pattern is [Lcom/company/package/Type
     */
    private static final String CUSTOMTYPEARRAYPATTERN = ".*\\[L.*(?<!String)$";
    /**
     * tracks the parameter order within a ';' separated types
     */
    private static final int INTRAORDEROFFSET = 50;
    /**
     * tracks the parameter order within types in complete signature
     */
    private static final int INTERORDEROFFSET = 100;
    /**
     * Key-> Position of the type in method signature, helps in the eventual sorting
     * Value-> Type
     */
    private Map<Integer, String> typeAndPositionMap = null;

    /**
     * an Enum of Primitive types and their corresponding string representation.
     * Helps in converting from Primitive type representation
     * to the representation expected by MUBench
     */
    public enum PrimitiveTypeRepresentation {
        BYTE(TYPEBYTEASCHAR, TYPEBYTEASSTRING),
        CHARACTER(TYPECHARACTERASCHAR, TYPECHARACTERASSTRING),
        DOUBLE(TYPEDOUBLEASCHAR, TYPEDOUBLEASSTRING),
        FLOAT(TYPEFLOATASCHAR, TYPEFLOATASSTRING),
        INT(TYPEINTASCHAR, TYPEINTASSTRING),
        LONG(TYPELONGASCHAR, TYPELONGASSTRING),
        SHORT(TYPESHORTASCHAR, TYPESHORTASSTRING),
        BOOLEAN(TYPEBOOLEANASCHAR, TYPEBOOLEANASSTRING);

        private char typeAsChar;
        private String typeAsString;

        PrimitiveTypeRepresentation(char typeInChar, String typeInString) {
            this.typeAsChar = typeInChar;
            this.typeAsString = typeInString;
        }

        public String getStringType() {
            return typeAsString;
        }

        /**
         * https://stackoverflow.com/questions/604424/lookup-enum-by-string-
         * value
         */
        public static PrimitiveTypeRepresentation convertToPrimitiveType(char basicType) {
            for (PrimitiveTypeRepresentation t : PrimitiveTypeRepresentation.values()) {
                if (t.typeAsChar == basicType)
                    return t;
            }
            return null;
        }

    }

    /**
     * adds <K,V> pair to the map, explicitly handles if the parameter is of array type
     *
     * @param param    the parameter type
     * @param isArray  {@code true} if the parameter an array, {@code false} otherwise
     * @param location the location of parameter in the method signature
     */
    private void addToStringBuilder(String param, boolean isArray, int location) {
        if (isArray) {
            param = param + "[]";
        }
        param = param + ", ";
        typeAndPositionMap.put(location, param);
    }

    /**
     * Extracts the basic type using {@link PrimitiveTypeRepresentation}
     *
     * @param basicType the basic type in Findbugs format
     * @param isArray   {@code true} if the parameter an array, {@code false} otherwise
     * @param location  the location of parameter in the method signature
     */
    private void extractBasicType(String basicType, boolean isArray, int location) {
        char c = (isArray) ? basicType.charAt(1) : basicType.charAt(0);
        PrimitiveTypeRepresentation typeCharacters = PrimitiveTypeRepresentation.convertToPrimitiveType(c);
        if (typeCharacters != null) {
            addToStringBuilder(typeCharacters.getStringType(), isArray, location);
        }
    }

    /**
     * Extracts String type
     *
     * @param stringType the string type in Findbugs format
     * @param isArray    {@code true} if the parameter an array, {@code false} otherwise
     * @param location   the location of parameter in the method signature
     */
    private void extractStringType(String stringType, boolean isArray, int location) {
        int startIndex = stringType.lastIndexOf('/') + 1;
        String extractedString = stringType.substring(startIndex);
        addToStringBuilder(extractedString, isArray, location + INTRAORDEROFFSET);
    }

    /**
     * Extracts Custom type
     *
     * @param customType the custom type in Findbugs format
     * @param isArray    {@code true} if the parameter an array, {@code false} otherwise
     * @param location   the location of parameter in the method signature
     */
    private void extractCustomType(String customType, boolean isArray, int location) {
        int startIndex = customType.lastIndexOf('/') + 1;
        String extractedString = customType.substring(startIndex);
        int dollarIndex = extractedString.indexOf('$');
        if (dollarIndex != -1) {
            extractedString = extractedString.substring(dollarIndex + 1);
        }
        addToStringBuilder(extractedString, isArray, location + INTRAORDEROFFSET);
    }

    // for identifying false positive of basic types, for eg: "[SLorg/test/govind/SType;"
    // where expected o/p is: "short, SType" and not "short, short, Stype"
    private boolean isNotFalsePositiveBasic(String type, int index) {
        String prefix = type.substring(0, index);
        return prefix.length() == 0 || !prefix.contains("/");
    }

    /**
     * Helper method that does pattern matching and calls the appropriate extractor
     *
     * @param type     the parameter type
     * @param regex    the regex used for pattern matching
     * @param location the location for order
     */
    private void extractType(String type, String regex, int location) {
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(type);
        while (matcher.find()) {
            String matchedString = matcher.group();
            switch (regex) {
                case STRINGARRAYPATTERN:
                    extractStringType(matchedString, true, location);
                    break;
                case STRINGPATTERN:
                    extractStringType(matchedString, false, location);
                    break;
                case CUSTOMTYPEARRAYPATTERN:
                    extractCustomType(matchedString, true, location);
                    break;
                case CUSTOMTYPEPATTERN:
                    extractCustomType(matchedString, false, location);
                    break;
                case BASICTYPEARRAYPATTERN:
                    if (isNotFalsePositiveBasic(type, matcher.start())) {
                        extractBasicType(matchedString, true, location + matcher.start());
                    }
                    break;
                case BASICTYPEPATTERN:
                    if (isNotFalsePositiveBasic(type, matcher.start())) {
                        extractBasicType(matchedString, false, location + matcher.start());
                    }
                    break;
                default:
                    System.out.println("not a string");
                    break;
            }
        }
    }

    /**
     * Converts from the method representation in Findbugs to method representation in MUBench
     *
     * @param findbugsSignature the method signature in Findbugs
     * @return the converted method signature as required by MuBench
     */
    public String convert(String findbugsSignature) {
        // builds the eventual converted string as per MUBench expectation
        StringBuilder finalParams = new StringBuilder();
        typeAndPositionMap = new TreeMap<>();
        if (findbugsSignature.charAt(0) != '(')
            return null;
        String params;
        params = findbugsSignature.substring(1, findbugsSignature.indexOf(')'));
        if (params.length() < 1)
            return params;
        String[] indivTypes = params.split(";");
        for (int i = 0; i < indivTypes.length; i++) {
            extractType(indivTypes[i], STRINGARRAYPATTERN, i * INTERORDEROFFSET);
            extractType(indivTypes[i], STRINGPATTERN, i * INTERORDEROFFSET);
            extractType(indivTypes[i], CUSTOMTYPEARRAYPATTERN, i * INTERORDEROFFSET);
            extractType(indivTypes[i], CUSTOMTYPEPATTERN, i * INTERORDEROFFSET);
            extractType(indivTypes[i], BASICTYPEARRAYPATTERN, i * INTERORDEROFFSET);
            extractType(indivTypes[i], BASICTYPEPATTERN, i * INTERORDEROFFSET);
        }
        // sort the keys and add the values to the builder
        for (Entry<Integer, String> entry : typeAndPositionMap.entrySet()) {
            finalParams.append(entry.getValue());
        }
        // remove the trailing ", "
        if (finalParams.length() > 0) {
            finalParams.setLength(finalParams.length() - 2);
        }
        return finalParams.toString();
    }
}
