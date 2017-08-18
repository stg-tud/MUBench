import org.apache.jackrabbit.core.ItemData;
import org.apache.jackrabbit.core.state.ItemState;

import javax.jcr.AccessDeniedException;
import javax.jcr.InvalidItemStateException;
import javax.jcr.RepositoryException;

class CheckStateNotNull {
  void canRead(ItemData data) throws AccessDeniedException, RepositoryException {
    ItemState state = data.getState();
    if (state == null) {
      throw new InvalidItemStateException(data.getId().toString());
    }
    if (state.getStatus() == ItemState.STATUS_NEW) {
      // do something...
    }
  }
}
