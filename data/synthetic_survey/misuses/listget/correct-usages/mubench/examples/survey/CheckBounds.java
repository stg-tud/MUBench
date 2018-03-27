package mubench.examples.survey;

import java.util.List;

public class CheckBounds {
	Object size(List<Object> l, int i) {
		if (0 <= i && i < l.size()) {
		  return l.get(i);
		} else {
		  return null;
		}
	}
}
