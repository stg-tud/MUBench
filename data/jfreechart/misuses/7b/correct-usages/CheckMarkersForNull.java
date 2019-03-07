import java.util.ArrayList;
import java.util.Map;

import org.jfree.chart.plot.Marker;

class CheckMarkersForNull {
  void pattern(Map foregroundDomainMarkers, int index, Marker marker) {
    ArrayList markers = (ArrayList) foregroundDomainMarkers.get(new Integer(index));
    if (markers != null) {
      markers.remove(marker);
    }
  }
}
