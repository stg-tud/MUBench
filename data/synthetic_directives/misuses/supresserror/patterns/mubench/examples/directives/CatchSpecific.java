package mubench.examples.directives;

import java.text.ParseException;

import mubench.examples.directives.SupressError.Target;

public class CatchSpecific {
	public void pattern(Target target) {
		byte[] data = null;
		try {
			data = target.loadData();
		} catch (ParseException t) {
			data = new byte[0];
		}
		// use data..
	}
}
