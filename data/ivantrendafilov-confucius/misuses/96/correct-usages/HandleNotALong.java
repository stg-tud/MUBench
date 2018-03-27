
class HandleNotALong {
  long pattern(String s) {
    try {
        return Long.parseLong(s);
    } catch (NumberFormatException e) {
      throw new NumberFormatException(String.format("Input string [%s] is not a parseable long", s));
    }
  }
}
