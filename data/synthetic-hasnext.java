import java.util.Collection;
import java.util.Iterator;

public class HasNext {
  public Object misuse(Collection<Object> os) {
		Iterator<Object> itr = os.iterator();
		return itr.next();
	}

	public Object hasNext(Collection<Object> os) {
		Iterator<Object> itr = os.iterator();
		return itr.hasNext() ? itr.next() : new Object();
	}

	public Object isEmpty(Collection<Object> os) {
		Iterator<Object> itr = os.iterator();
		return !os.isEmpty() ? itr.next() : new Object();
	}

	public Object size(Collection<Object> os) {
		Iterator<Object> itr = os.iterator();
		return os.size() != 0 ? itr.next() : new Object();
	}

	public Object add(Collection<Object> os) {
		os.add(new Object());
		Iterator<Object> itr = os.iterator();
		return itr.next();
	}
}
