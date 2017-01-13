import java.util.Collection;
import java.util.Iterator;

public class Add {
	void pattern(Collection<Object> os, Object def) {
		os.add(def);
		Iterator<Object> itr = os.iterator();
		itr.next();
	}
}
