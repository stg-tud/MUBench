import java.util.HashMap;

public class CheckKeyNotNull {
	public void pattern(HashMap<String, Object> m, String key) {
		if (key != null) {
			m.get(key);
		}
	}
}
