package com.google.javascript.rhino.jstype;

import com.google.javascript.rhino.jstype.UnionTypeBuilder;
import com.google.javascript.rhino.jstype.JSType;

public class IsNotType {	
	public JSType pattern(UnionTypeBuilder builder) {
    JSType result = builder.build();
    if(!result.isNoType()) {
      return result;
    } else {
      return null; // default value
    }
	}
}
