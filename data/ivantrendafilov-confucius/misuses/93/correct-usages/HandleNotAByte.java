
class HandleNotAByte {
  long pattern(String s) {
    try {
        return Byte.parseByte(s);
    } catch (NumberFormatException e) {
      throw new NumberFormatException(String.format("Input string [%s] is not a parseable byte", s));
    }
  }
}
