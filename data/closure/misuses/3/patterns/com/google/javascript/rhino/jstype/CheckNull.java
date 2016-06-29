package com.google.javascript.rhino.jstype;

import com.google.common.collect.ImmutableSet;
import com.google.javascript.rhino.jstype.ObjectType;

import java.util.Set;

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