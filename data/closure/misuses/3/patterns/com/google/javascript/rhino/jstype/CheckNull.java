
class CheckNull {
  void pattern(ObjectType interfaceType) {
    ObjectType proto = interfaceType.getImplicitPrototype();
    if (proto == null) {
      // do fallback handling...
    } else {
      // do you thing
    }
  }
}