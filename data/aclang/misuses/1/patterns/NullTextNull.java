import org.apache.commons.lang.text.StrBuilder;

class NullTextNull extends StrBuilder {
  String pattern(Object obj) {
    String str = (obj == null ? this.getNullText() : obj.toString());
    if (str == null) {
      str = "";
    }
    return str;
  }
}
