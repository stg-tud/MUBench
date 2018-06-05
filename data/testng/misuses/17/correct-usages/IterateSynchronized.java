import java.util.List;
import java.util.ArrayList;
import java.util.Collections;

import org.testng.ITestResult;
import org.testng.internal.Utils;

class IterateSynchronized {
  private List<ITestResult> syncL = Collections.synchronizedList(new ArrayList<ITestResult>());
  
  void pattern() {
    synchronized(syncL) {
      for (ITestResult tr : syncL) {
        long elapsedTimeMillis= tr.getEndMillis() - tr.getStartMillis();
        String name= tr.getMethod().isTest() ? tr.getName() : Utils.detailedMethodName(tr.getMethod(), false);
      }
    }
  }
}
