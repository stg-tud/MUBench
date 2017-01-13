import org.apache.commons.collections.BeanMap;

import java.util.Iterator;
import java.util.Properties;

class UseContainsKeyOverGetNotNull {
  void pattern(BeanMap map, String key) {
    if (!map.containsKey(key)) {
      // map does not contain key
    }
  }
}
