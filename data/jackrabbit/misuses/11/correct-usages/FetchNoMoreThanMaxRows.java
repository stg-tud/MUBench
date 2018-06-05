import java.sql.PreparedStatement;

class FetchNoMoreThanMaxRows {
  void pattern(PreparedStatement stmt) {
    stmt.setMaxRows(maxRows);
    int fetchSize = 10000;
    if (0 < maxRows && maxRows < fetchSize) {
      fetchSize = maxRows; // JCR-3090
    }
    stmt.setFetchSize(fetchSize);
  }
}