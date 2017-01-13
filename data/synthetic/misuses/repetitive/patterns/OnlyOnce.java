import java.util.Collection;

public class OnlyOnce {
	void pattern(Collection<Object> objects) {
		if (!objects.isEmpty()) {
			objects.iterator().next();
		}
	}
}
