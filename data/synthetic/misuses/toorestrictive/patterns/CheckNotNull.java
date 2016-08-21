import java.util.List;

public class TooRestrictive {
	public void pattern(List<String> l) {
		for (int i = 1; i <= l.size(); i++) {
			System.out.println("Element #" + i + " is '" + l.get(i -1) + "'");
		}
	}
}
