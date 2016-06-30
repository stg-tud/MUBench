import java.util.Collection;
import java.util.Iterator;

public class Add {
	public Object pattern(Collection<Object> os, Object def) {
		os.add(def);
		Iterator<Object> itr = os.iterator();
		return itr.next();
	}
}
