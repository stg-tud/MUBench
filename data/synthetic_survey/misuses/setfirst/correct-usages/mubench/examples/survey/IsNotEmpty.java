package mubench.examples.survey;

import java.util.Set;

public class IsNotEmpty {
	void pattern(Set<Object> set) {
		if (!set.isEmpty()) {
			set.iterator().next();
		}
	}
}
