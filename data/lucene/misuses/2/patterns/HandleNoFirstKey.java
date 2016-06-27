import java.util.*;

class HandleNoFirstKey {
  Object pattern(SortedMap fieldToReader) {
    String field;
    try {
      field = (String)fieldToReader.firstKey();
    } catch(NoSuchElementException e) {
      return null;
    }
    if (field != null) {
      return fieldToReader.get(field);
    }
  }
}