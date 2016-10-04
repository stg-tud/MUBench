import java.util.Map;
import java.util.ArrayList;

import org.jfree.chart.plot.Marker;

class CheckMarkersForNull {
  boolean pattern(Map domainMarkers, int index, Marker marker) {
    ArrayList markers = (ArrayList) domainMarkers.get(new Integer(index));
    if (markers == null) {
      return false;
    }
    return markers.remove(marker);
  }
}