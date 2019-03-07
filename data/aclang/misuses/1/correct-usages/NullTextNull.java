import org.apache.commons.lang.text.StrBuilder;

class NullTextNull extends StrBuilder {
  void pattern(Object obj) {
    String str = (obj == null ? this.getNullText() : obj.toString());
    if (str != null) {
      str.length();
    }
  }
}
