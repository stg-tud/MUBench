import java.util.HashMap;

public class CheckKeyNotNull {
	public Object pattern(HashMap<String, Object> m, String key) {
		if (key != null) {
			return m.get(key);
		} else {
		  return null;
		}
	}
}
