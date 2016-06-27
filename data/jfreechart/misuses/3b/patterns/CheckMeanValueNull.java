import org.jfree.data.statistics.StatisticalCategoryDataset;

class CheckMeanValueNull {
  void pattern(StatisticalCategoryDataset dataset) {
    Number meanValue = dataset.getMeanValue(row, column);
    if (meanValue == null) {
      return;
    }
    return meanValue.doubleValue();
  }
}
