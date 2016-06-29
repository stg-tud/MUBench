import org.jfree.data.statistics.StatisticalCategoryDataset;

class CheckMeanValueNull {
  double pattern(StatisticalCategoryDataset dataset, int row, int column) {
    Number meanValue = dataset.getMeanValue(row, column);
    if (meanValue == null) {
      return 0;
    }
    return meanValue.doubleValue();
  }
}
