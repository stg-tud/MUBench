import org.apache.jackrabbit.core.ItemData;
import org.apache.jackrabbit.core.ItemId;
import org.apache.jackrabbit.core.SessionImpl;
import org.apache.jackrabbit.core.state.ItemState;
import org.apache.jackrabbit.spi.Path;

import javax.jcr.AccessDeniedException;
import javax.jcr.InvalidItemStateException;
import javax.jcr.RepositoryException;

class CheckStateNotNull {
  boolean canRead(ItemData data, Path path, SessionImpl session) throws AccessDeniedException, RepositoryException {
    ItemState state = data.getState();
    if (state == null) {
        throw new InvalidItemStateException(data.getId() + ": the item does not exist anymore");
    }
    if (state.getStatus() == ItemState.STATUS_NEW && !data.getDefinition().isProtected()) {
        return true;
    } else {
        return (path == null) ? canRead(data.getId()) : session.getAccessManager().canRead(path);
    }
  }
  
  private boolean canRead(ItemId id) { return true; }
}