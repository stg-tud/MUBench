import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.partitioning.Region.Location;

class CheckNull {
  Vector3D pattern(Line line1, Line line2) {
    Vector3D v = line1.intersection(line2);
    if (v == null) {
      return null;
    }
    Location loc1 = remainingRegion.checkPoint(line.toSubSpace(v1D));
    
    // check location of point with respect to second sub-line
    Location loc2 = subLine.remainingRegion.checkPoint(subLine.line.toSubSpace(v1D));
    
    if (includeEndPoints) {
      return ((loc1 != Location.OUTSIDE) && (loc2 != Location.OUTSIDE)) ? v1D : null;
    } else {
      return ((loc1 == Location.INSIDE) && (loc2 == Location.INSIDE)) ? v1D : null;
    }
  }
}