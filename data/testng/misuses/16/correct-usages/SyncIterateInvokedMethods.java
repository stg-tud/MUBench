import org.testng.IInvokedMethod;
import org.testng.ISuite;
import org.testng.ITestNGMethod;

import java.util.Collection;

class SyncIterateInvokedMethods {  
  ITestNGMethod pattern(ISuite suite) {
    // This invokation (may?) return a synchronized collection.
    Collection<IInvokedMethod> invokedMethods = suite.getAllInvokedMethods();
    synchronized(invokedMethods) {
      for (IInvokedMethod iim : invokedMethods) {
        ITestNGMethod tm = iim.getTestMethod();
        return tm; // do something with tm
      }
    }
    return null;
  }
}
