package com.google.javascript.rhino.jstype;

import com.google.javascript.rhino.jstype.UnionTypeBuilder;
import com.google.javascript.rhino.jstype.JSType;

public class IsNotType {	
	public boolean pattern(UnionTypeBuilder builder) {
    JSType result = builder.build();
    return result.isNoType();
	}
}
