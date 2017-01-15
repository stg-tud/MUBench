import org.jfree.chart.plot.CategoryPlot;
import org.jfree.data.category.CategoryDataset;

class CheckDatasetForNull {
  void pattern(CategoryPlot plot, int index) {
    CategoryDataset dataset = plot.getDataset(index);
    if (dataset != null) {
      dataset.getRowCount();
    }
  }
}
