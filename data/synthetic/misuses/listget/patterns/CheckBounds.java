import java.util.List;

public class CheckBounds {
	void size(List<Object> l, int i) {
		if (0 <= i && i < l.size()) {
		  l.get(i);
		}
	}
}
