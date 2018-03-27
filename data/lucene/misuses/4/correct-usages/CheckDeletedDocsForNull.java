import org.apache.lucene.benchmark.byTask.PerfRunData;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.MultiFields;
import org.apache.lucene.util.Bits;

class CheckDeletedDocsForNull {
  int pattern(PerfRunData runData) throws Exception {
    IndexReader r = runData.getIndexReader();
    int maxDoc = r.maxDoc();
    int numDeleted = 0;
    // percent is an absolute target:
    int numToDelete = ((int) (maxDoc * percent)) - r.numDeletedDocs();
    if (numToDelete < 0) {
      r.undeleteAll();
      numToDelete = (int) (maxDoc * percent);
    }
    while (numDeleted < numToDelete) {
      double delRate = ((double) (numToDelete-numDeleted))/r.numDocs();
      Bits delDocs = MultiFields.getDeletedDocs(r);
      int doc = 0;
      while (doc < maxDoc && numDeleted < numToDelete) {
        if ((delDocs == null || !delDocs.get(doc)) && random.nextDouble() <= delRate) {
          r.deleteDocument(doc);
          numDeleted++;
          if (delDocs == null) {
            delDocs = MultiFields.getDeletedDocs(r);
            assert delDocs != null;
          }
        }
        doc++;
      }
    }
    r.decRef();
    return numDeleted;
  }
}