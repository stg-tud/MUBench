import java.util.Collection;
import java.util.Iterator;

public class DoNotModify {
  public void pattern(Collection<Object> c, Object element) {
  	Iterator<Object> i = c.iterator();
  	if (i.hasNext())
  		i.next();
  }
}
