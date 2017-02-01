import java.util.Collection;
import java.util.Iterator;

public class OnlyNext {
  public Object misuse(Collection<Object> os) {
		Iterator<Object> itr = os.iterator();
		return itr.next();
	}
}
