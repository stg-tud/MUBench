import java.util.*;

class HandleNoFirstKey {
  void pattern(SortedMap fieldToReader) {
    try {
      fieldToReader.firstKey();
    } catch(NoSuchElementException e) {
      // ...
    }
  }
}
