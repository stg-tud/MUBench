import java.util.Collection;
import java.util.Iterator;

public class CME {
  public void misuse(Collection<Object> c) {
  	Iterator<Object> i = c.iterator();
  	c.add(new Object());
  	if (i.hasNext())
  		i.next();
  }
}
