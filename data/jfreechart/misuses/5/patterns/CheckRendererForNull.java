
class CheckRendererForNull {
  void pattern(XYDataset d, XYPlot plot) {
    XYItemRenderer r = plot.getRendererForDataset(d);
    if (r != null) {
      Collection c = r.getAnnotations();
    }
  }
}