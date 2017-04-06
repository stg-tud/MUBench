package de.tu_darmstadt.stg.mubench.cli;

@SuppressWarnings("WeakerAccess")
public class CodePath {
	public final String srcPath;
	public final String classPath;
	
	public CodePath(String srcPath, String classPath) {
		this.srcPath = srcPath;
		this.classPath = classPath;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((classPath == null) ? 0 : classPath.hashCode());
		result = prime * result + ((srcPath == null) ? 0 : srcPath.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		CodePath other = (CodePath) obj;
		if (classPath == null) {
			if (other.classPath != null)
				return false;
		} else if (!classPath.equals(other.classPath))
			return false;
		if (srcPath == null) {
			if (other.srcPath != null)
				return false;
		} else if (!srcPath.equals(other.srcPath))
			return false;
		return true;
	}

	@Override
	public String toString() {
		return "CodePath [srcPath=" + srcPath + ", classPath=" + classPath + "]";
	}
}
