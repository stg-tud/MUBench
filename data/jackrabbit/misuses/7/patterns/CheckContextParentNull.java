import org.apache.jackrabbit.core.state.ItemStateManager;
import org.apache.jackrabbit.core.state.NodeState;

class CheckContextParentNull {
  NodeState pattern(NodeState context, ItemStateManager ism) {
    return context.getParentId() == null ? null : (NodeState) ism.getItemState(context.getParentId());
  }
}