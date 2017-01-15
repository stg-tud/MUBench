import java.util.Map;
import java.util.ArrayList;

import org.jfree.chart.plot.Marker;

class CheckMarkersForNull {
  void pattern(Map domainMarkers, int index, Marker marker) {
    ArrayList markers = (ArrayList) domainMarkers.get(new Integer(index));
    if (markers != null) {
      markers.remove(marker);
    }
  }
}
