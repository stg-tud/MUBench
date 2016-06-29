import org.jfree.chart.plot.CategoryPlot;
import org.jfree.data.category.CategoryDataset;

class CheckDatasetForNull {
  int pattern(CategoryPlot plot, int index) {
    CategoryDataset dataset = plot.getDataset(index);
    if (dataset == null) {
      return 0; // default value
    }
    return dataset.getRowCount();
  }
}