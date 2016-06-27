import org.jfree.data.statistics.StatisticalCategoryDataset;

class CheckMeanValueNull {
  void pattern(StatisticalCategoryDataset dataset) {
    Number n = dataset.getStdDevValue(row, column);
    if (n != null) {
        double valueDelta = n.doubleValue();
        // do something with valueDelta...
    }
  }
}
