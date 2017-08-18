import java.util.HashMap;

public class MapKeyNull {
	Object misuse(HashMap<String, Object> m, String key) {
		return m.get(key);
	}
}
