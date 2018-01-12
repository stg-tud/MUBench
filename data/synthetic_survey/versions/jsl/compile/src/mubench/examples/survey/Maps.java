package mubench.examples.survey;

import java.util.HashMap;
import java.util.Map;

public class Maps {
	Object keyMayBeNull(HashMap<String, Object> m, String key) {
		return m.get(key);
	}
  
	void mapMayContainNull(Map<String, Object> m) {
		if (m.put("foo", new Object()) != null) {
			// "foo" was set before
		} else {
			// "foo" was not set before (or set to null!)
		}
	}
}
