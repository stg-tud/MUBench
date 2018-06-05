package mubench.examples.directives;

public class WaitWithoutLoop {
	void misuse(Target t) throws InterruptedException {
    synchronized (t) {
      if (t.isAvailable()) {
        t.wait();
      }
      // Perform action appropriate to condition
    }
	}
  
  static class Target {
    boolean isAvailable() { return false; }
  }
}
