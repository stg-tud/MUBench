
class HandleNotAShort {
  long pattern(String s) {
    try {
        return Short.parseShort(s);
    } catch (NumberFormatException e) {
      throw new NumberFormatException(String.format("Input string [%s] is not a parseable short", s));
    }
  }
}
