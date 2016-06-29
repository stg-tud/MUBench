import org.apache.commons.collections.BeanMap;

import java.util.Iterator;
import java.util.Properties;

class UseContainsKeyOverGetNotNull {
  Object pattern(BeanMap map, Properties properties) {
    Iterator iterator = map.keyIterator();
    while (iterator.hasNext()) {
       String name = (String) iterator.next();
       String value = properties.getProperty(name);
       if (value != null) {
           map.put(name, properties.getProperty(name));
       }
    }
    Iterator it = properties.keySet().iterator();
    while (it.hasNext()) {
       String key = (String) it.next();
       if (!map.containsKey(key) && properties.getProperty(key) != null) {
         // do something...
       }
    }
  }
}