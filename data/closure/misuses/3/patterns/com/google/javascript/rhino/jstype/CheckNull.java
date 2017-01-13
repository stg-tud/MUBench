package com.google.javascript.rhino.jstype;

import com.google.javascript.rhino.jstype.ObjectType;

class CheckNull {
  void pattern(ObjectType interfaceType) {
    ObjectType implicitProto = interfaceType.getImplicitPrototype();
    if (implicitProto != null) {
      implicitProto.getOwnPropertyNames();
    }
  }
}
