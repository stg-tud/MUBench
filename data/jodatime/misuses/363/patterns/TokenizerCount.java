
import java.util.StringTokenizer;

class TokenizerCount {
  String pattern(StringTokenizer st) {
    if (st.countTokens() < 1) {
      throw new IllegalArgumentException("too few tokens");
    }
    return st.nextToken();
  }
}
