import org.apache.jackrabbit.core.ItemId;
import org.apache.jackrabbit.core.state.ItemStateManager;
import org.apache.jackrabbit.core.state.NodeState;

class CheckContextParentNull {
  void pattern(NodeState context, ItemStateManager ism) {
    NodeId parentId = context.getParentId()
    if (parentId != null) {
      ism.getItemState(parentId);
    }
  }
}
