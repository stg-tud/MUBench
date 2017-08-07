class HandleNotANumber {
  long pattern(String value) {
    try {
      return Long.parseLong(value);
    } catch (NumberFormatException e) {
      // throw more expressive error
      throw new NumberFormatException(String.format("Value [%s] is not a parseable Long", value));
    }
  }
}
