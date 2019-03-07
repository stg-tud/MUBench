package mubench.examples.directives;

import java.util.Set;

import mubench.examples.directives.WaitWithoutLoop.Target;

public class WaitLoop {
	void pattern(Target t) throws InterruptedException {
    synchronized (t) {
      while (t.isAvailable()) {
        t.wait();
      }
      // Perform action appropriate to condition
    }
	}
}
