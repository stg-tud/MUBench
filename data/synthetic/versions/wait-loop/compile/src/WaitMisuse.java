import java.util.Set;

public class WaitMisuse {
	public void misuse(Object obj) throws InterruptedException {
    synchronized (obj) {
      if (isAvailable(obj)) {
        obj.wait();
      }
      // Perform action appropriate to condition
    }
	}
  
  private static boolean isAvailable(Object o) { return false; }
}
