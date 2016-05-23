import java.util.Collection;
import java.util.Iterator;

public class IsEmpty {
	public Object pattern(Collection<Object> os, Object def) {
		Iterator<Object> itr = os.iterator();
		return !os.isEmpty() ? itr.next() : def;
	}
}
