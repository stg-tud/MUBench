import java.util.Collection;
import java.util.Iterator;

public class AddBefore {
  public void pattern(Collection<Object> c, Object element) {
    c.add(element);
  	Iterator<Object> i = c.iterator();
  	if (i.hasNext())
  		i.next();
  }
}
