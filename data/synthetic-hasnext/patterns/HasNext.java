import java.util.Collection;
import java.util.Iterator;

public class HasNext {
	public Object pattern(Collection<Object> os, Object def) {
		Iterator<Object> itr = os.iterator();
		return itr.hasNext() ? itr.next() : def;
	}
}
