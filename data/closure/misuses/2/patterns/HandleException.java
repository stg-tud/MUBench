import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.spi.Parameters;

class HandleException {
  void pattern(Parameters params) {
    String param = null;
    try {
      param = params.getParameter(0);
    } catch (CmdLineException e) {
      // handle exception...
    }
    if (param == null) {
      // do something...
    } else {
      String lowerParam = param.toLowerCase();
      // do something else...
    }
  }
}