import java.util.Map;

public class MapNull {

	public void misuse(Map<String, Object> m) {
		if (m.put("foo", new Object()) != null) {
			// "foo" was set before
		} else {
			// "foo" was not set before (or set to null!)
		}
	}
	
	public void containsKey(Map<String, Object> m) {
		if (m.containsKey("foo")) {
			m.put("foo", new Object());
			// "foo" was set before
		} else {
			m.put("foo", new Object());
			// "foo" was not set before
		}
	}
}
