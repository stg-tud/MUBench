import java.util.Collection;
import java.util.Iterator;

public class Size {
	public Object pattern(Collection<Object> os, Object def) {
		Iterator<Object> itr = os.iterator();
		return os.size() != 0 ? itr.next() : def;
	}
}
