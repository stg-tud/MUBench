import org.apache.lucene.index.IndexReader;

import java.io.IOException;

import java.util.Map;
import java.util.HashMap;

abstract class UseKeyForMapRetrieve {
  Object get(Map readerCache, IndexReader reader, Object key) throws IOException {
    Map innerCache;
    Object value;
    synchronized (readerCache) {
      innerCache = (Map) readerCache.get(reader);
      if (innerCache == null) {
        innerCache = new HashMap();
        readerCache.put(reader, innerCache);
        value = null;
      } else {
        value = innerCache.get(key);
      }
      if (value == null) {
        value = new CreationPlaceholder();
        innerCache.put(key, value);
      }
    }
    if (value instanceof CreationPlaceholder) {
      synchronized (value) {
        CreationPlaceholder progress = (CreationPlaceholder) value;
        if (progress.value == null) {
          progress.value = createValue(reader, key);
          synchronized (readerCache) {
            innerCache.put(key, progress.value);
          }
        }
        return progress.value;
      }
    }
    return value;
  }
  
  Object createValue(IndexReader reader, Object key) throws IOException {
    return null; // stub
  }
  
  static final class CreationPlaceholder {
    Object value;
  }
}