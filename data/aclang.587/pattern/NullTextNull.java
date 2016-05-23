Object obj;
org.apache.commons.lang.text.StrBuilder builder;
String str = (obj == null ? builder.getNullText() : obj.toString());
if (str == null) {
    str = "";
}
str.length()