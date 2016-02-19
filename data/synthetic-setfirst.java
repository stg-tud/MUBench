import java.util.Set;

public class SetFirst {

	public Object misuse(Set<Object> set) {
		return set.iterator().next();
	}

	public Object isEmpty(Set<Object> set) {
		if (!set.isEmpty()) {
			return set.iterator().next();
		} else {
			return new Object(); // some default value
		}
	}
}