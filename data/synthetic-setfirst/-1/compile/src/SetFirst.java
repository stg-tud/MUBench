import java.util.Set;

public class SetFirst {
	public Object misuse(Set<Object> set) {
		return set.iterator().next();
	}
}
