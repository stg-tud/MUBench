import org.apache.commons.math3.geometry.euclidean.twod.Line;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;

class CheckV2DNull {
  public Vector2D pattern(Line line, Line other) {
    Vector2D v2D = line.intersection(other);
    if (v2D == null) {
        return null;
    }
    line.toSubSpace(v2D);
    other.toSubSpace(v2D);
    return v2D;
  }
}
