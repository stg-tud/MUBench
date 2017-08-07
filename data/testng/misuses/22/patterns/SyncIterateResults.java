import org.testng.ISuite;
import org.testng.ISuiteResult;
import org.testng.ITestContext;

import java.util.Map;

class SyncIterateResults {  
  ITestContext pattern(ISuite suite) {
    // This invokation (may?) return a synchronized map.
    Map<String, ISuiteResult> results = suite.getResults();
    synchronized(results) {
      for (ISuiteResult sr : results.values()) {
        ITestContext context = sr.getTestContext();
        return context; // do something with context
      }
    }
    return null;
  }
}
