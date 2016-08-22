import java.util.Set;

public class WaitLoop {
	public void misuse(Object obj) throws InterruptedException {
    synchronized (obj) {
      while (isAvailable(obj)) {
        obj.wait();
      }
      // Perform action appropriate to condition
    }
	}
  
  private static boolean isAvailable(Object o) { return false; }
}
