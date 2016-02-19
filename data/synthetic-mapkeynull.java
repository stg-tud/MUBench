import java.util.HashMap;

public class MapKeyNull {

	public void misuse(HashMap<String, Object> m, String key) {
		m.get(key);
	}
	
	public void containsKey(HashMap<String, Object> m, String key) {
		if (key != null) {
			m.get(key);
		}
	}
}