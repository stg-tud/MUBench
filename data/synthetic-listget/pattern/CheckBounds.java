import java.util.List;

public class CheckBounds {
	public Object size(List<Object> l, int i, Object def) {
		if (0 <= i && i < l.size()) {
		  return l.get(i);
		} else {
		  return def;
		}
	}
}
