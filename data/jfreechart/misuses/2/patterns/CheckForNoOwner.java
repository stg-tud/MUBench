import org.jfree.chart.ChartRenderingInfo;
import org.jfree.chart.entity.EntityCollection;
import org.jfree.chart.plot.PlotRenderingInfo;

class CheckForNoOwner {
  void pattern(PlotRenderingInfo plotState) {
    ChartRenderingInfo owner = plotState.getOwner();
    if (owner != null) {
      EntityCollection entities = owner.getEntityCollection();
      // work with the entities...
    }
  }
}
