import java.util.Map;

public class Contains {
  public void pattern(Map<String, Object> m, String key, Object value) {
    if (m.containsKey(key)) {
      // key was set before
    } else {
      // key was not set before
      m.put(key, value);
    }
  }
}
