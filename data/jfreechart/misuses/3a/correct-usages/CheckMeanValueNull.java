import org.jfree.data.statistics.StatisticalCategoryDataset;

class CheckMeanValueNull {
  void pattern(StatisticalCategoryDataset dataset, int row, int column) {
    Number meanValue = dataset.getMeanValue(row, column);
    if (meanValue != null) {
      meanValue.doubleValue();
    }
  }
}
