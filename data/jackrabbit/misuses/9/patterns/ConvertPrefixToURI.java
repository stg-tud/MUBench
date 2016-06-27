import org.apache.jackrabbit.jcr2spi.NamespaceStorage;

class ConvertPrefixToURI {
  void pattern(NamespaceStorage storage, String prefix) {
    String uri = storage.getURI(prefix);
    storage.unregisterNamespace(uri);
  }
}