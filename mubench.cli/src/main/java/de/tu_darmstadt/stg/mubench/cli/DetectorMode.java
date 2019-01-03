package de.tu_darmstadt.stg.mubench.cli;

@SuppressWarnings("WeakerAccess")
public enum DetectorMode {
	MINE_AND_DETECT("0"),
	DETECT_ONLY("1");

	private final String code;

	DetectorMode(String code) {
		this.code = code;
	}

	protected String getCode() {
		return code;
	}

	protected static DetectorMode fromCode(String code) {
		for (DetectorMode mode : DetectorMode.values()) {
			if (mode.code.equals(code)) {
				return mode;
			}
		}
		throw new IllegalArgumentException("no such mode: '" + code + "'");
	}
}
