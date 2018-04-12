import java.util.Collection;
import java.util.Iterator;

import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYItemRenderer;
import org.jfree.data.xy.XYDataset;

class CheckRendererForNull {
  void pattern(XYDataset d, XYPlot plot) {
    XYItemRenderer r = plot.getRendererForDataset(d);
    if (r != null) {
      Collection c = r.getAnnotations();
      Iterator i = c.iterator();
      // use iterator...
    }
  }
}
