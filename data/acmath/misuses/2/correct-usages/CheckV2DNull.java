import org.apache.commons.math3.geometry.euclidean.twod.Line;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;

class CheckV2DNull {
  void pattern(Line line, Line other) {
    Vector2D v2D = line.intersection(other);
    if (v2D != null) {
      line.toSubSpace(v2D);
      other.toSubSpace(v2D);
    }
  }
}
