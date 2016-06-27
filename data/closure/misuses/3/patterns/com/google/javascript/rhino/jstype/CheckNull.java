import com.google.common.collect.ImmutableSet;
import com.google.javascript.rhino.jstype.ObjectType;

class CheckNull {
  Set<String> pattern(ObjectType interfaceType) {
    ObjectType proto = interfaceType.getImplicitPrototype();
    Set<String> currentPropertyNames;
    if (proto == null) {
      currentPropertyNames = ImmutableSet.of();
    } else {
      currentPropertyNames = implicitProto.getOwnPropertyNames();
    }
    return currentPropertyNames;
  }
}