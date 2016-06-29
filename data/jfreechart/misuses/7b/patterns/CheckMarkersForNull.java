import java.util.ArrayList;
import java.util.Map;

import org.jfree.chart.plot.Marker;

class CheckMarkersForNull {
  boolean pattern(Map foregroundDomainMarkers, int index, Marker marker) {
    ArrayList markers = (ArrayList) foregroundDomainMarkers.get(new Integer(index));
    if (markers == null) {
      return false;
    }
    return markers.remove(marker);
  }
}