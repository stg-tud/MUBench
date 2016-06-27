import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;

class CheckV3DNull {
  public Vector3D pattern(Line line, Line other) {
    Vector3D v1D = line.intersection(other);
    if (v1D == null) {
        return null;
    }
    line.toSubSpace(v1D);
    other.toSubSpace(v1D);
    return v1D;
  }
}