
class CheckMarkersForNull {
  boolean pattern(Map foregroundDomainMarkers, int index, Marker marker) {
    ArrayList markers = (ArrayList) foregroundDomainMarkers.get(new Integer(index));
    if (markers == null) {
      return false;
    }
    return markers.remove(marker);
  }
}