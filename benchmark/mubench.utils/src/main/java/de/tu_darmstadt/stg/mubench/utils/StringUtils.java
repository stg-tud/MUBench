package de.tu_darmstadt.stg.mubench.utils;

import java.util.List;

import com.google.common.base.Joiner;

public class StringUtils {
	public static String toString(List<String> lines) {
		return Joiner.on("\n").join(lines);
	}
}
