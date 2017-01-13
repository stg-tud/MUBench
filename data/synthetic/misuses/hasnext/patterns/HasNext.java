import java.util.Collection;
import java.util.Iterator;

public class HasNext {
	void pattern(Collection<Object> os) {
		Iterator<Object> itr = os.iterator();
		if (itr.hasNext()) {
      itr.next();
    }
	}
}
