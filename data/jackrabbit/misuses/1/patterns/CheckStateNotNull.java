import org.apache.jackrabbit.core.ItemData;
import org.apache.jackrabbit.core.state.ItemState;

import javax.jcr.AccessDeniedException;
import javax.jcr.InvalidItemStateException;
import javax.jcr.RepositoryException;

class CheckStateNotNull {
  void canRead(ItemData data) throws AccessDeniedException, RepositoryException {
    ItemState state = data.getState();
    if (state != null) {
        state.getStatus();
    }
  }
}
