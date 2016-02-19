import java.util.List;

public class ListGet {
	public Object misuse(List<Object> l, int i) {
		return l.get(i);
	}
  
	public Object size(List<Object> l, int i) {
		if (0 <= i && i < l.size()) {
		  return l.get(i);
		} else {
		  return l.get(l.size() - 1);
		}
	}
}