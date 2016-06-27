import org.apache.jackrabbit.jcr2spi.hierarchy.NodeEntry;
import org.apache.jackrabbit.jcr2spi.state.NodeState;

import javax.jcr.ItemNotFoundException;
import javax.jcr.RepositoryException;
  
class CheckHierarchyEntryHasParent {
  NodeState getParent() throws ItemNotFoundException, RepositoryException {
    NodeEntry parent = getHierarchyEntry().getParent();
    if (parent != null) {
        return getHierarchyEntry().getParent().getNodeState();
    }
    return null;
  }
}