import java.util.Collection;

public class OnlyOnce {
	public String pattern(Collection<Object> objects) {
		String value = null;
		if (!objects.isEmpty()) {
			value = objects.iterator().next().toString();
		}
		return value;
	}
}
