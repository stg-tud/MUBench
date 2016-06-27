import org.apache.commons.lang.text.StrBuilder;

class NullTextNull extends StrBuilder {
  String pattern(Object obj) {
    this.ensureCapacity(size + width);
    String str = (obj == null ? this.getNullText() : obj.toString());
    if (str == null) {
      str = "";
    }
    return str;
  }
}
