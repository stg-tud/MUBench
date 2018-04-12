import org.apache.jackrabbit.jcr2spi.hierarchy.NodeEntry;

import javax.jcr.ItemNotFoundException;
import javax.jcr.RepositoryException;
  
class CheckHierarchyEntryHasParent {
  void getParent() throws ItemNotFoundException, RepositoryException {
    NodeEntry parent = getHierarchyEntry().getParent();
    if (parent != null) {
        parent.getNodeState();
    }
  }
}
