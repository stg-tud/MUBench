import org.apache.commons.lang.text.StrBuilder;

public class NullTextNull {
  
  public String pattern(Object obj, StrBuilder builder) {
    String str = (obj == null ? builder.getNullText() : obj.toString());
    if (str == null) {
      str = "";
    }
    return str;
  }
}
