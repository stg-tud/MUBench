import java.util.List;

public class TooRestrictive {
	public void misuse(List<String> l) {
		for (int i = 1; i < l.size(); i++) {
			l.get(i - 1); // the last element of this list is never retrieved
		}
	}
}
