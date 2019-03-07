import java.util.*;

class HandleNoFirstKey {
  void pattern(SortedMap fieldToReader) {
    String field;
    try {
      field = (String) fieldToReader.firstKey();
    } catch(NoSuchElementException e) {
      return;
    }
    if (field != null) {
      // do something with field...
    }
  }
}
