import java.util.Collection;

public class Repetitive {
	public String misuse(Collection<Object> objects) {
		String value = null;
		for (Object object : objects) {
			value = objects.iterator().next().toString();
		}
		return value;
	}
}
