package com.google.javascript.rhino.jstype;

import com.google.javascript.rhino.jstype.ObjectType;
import com.google.common.collect.ImmutableSet;

import java.util.Set;

class CheckNull {
  void pattern(ObjectType interfaceType) {
    ObjectType implicitProto = interfaceType.getImplicitPrototype();
    Set<String> currentPropertyNames;
    if (implicitProto == null) {
      currentPropertyNames = ImmutableSet.of();
    } else {
      currentPropertyNames = implicitProto.getOwnPropertyNames();
    }
    for (String name : currentPropertyNames) {
      // do something with the name...
    }
  }
}
