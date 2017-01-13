import org.apache.lucene.index.IndexReader;

import java.io.IOException;

import java.util.Map;
import java.util.HashMap;

abstract class UseKeyForMapRetrieve {
  void get(Map innerCache, Object key) throws IOException {
    Object value;
    if (innerCache == null) {
      innerCache = new HashMap();
      value = null;
    } else {
      value = innerCache.get(key);
    }
    if (value == null) {
      value = new CreationPlaceholder();
      innerCache.put(key, value);
    }
  }
  
  static final class CreationPlaceholder {
    Object value;
  }
}
