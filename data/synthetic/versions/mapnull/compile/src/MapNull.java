import java.util.Map;

public class MapNull {
	public void misuse(Map<String, Object> m) {
		if (m.put("foo", new Object()) != null) {
			// "foo" was set before
		} else {
			// "foo" was not set before (or set to null!)
		}
	}
}
