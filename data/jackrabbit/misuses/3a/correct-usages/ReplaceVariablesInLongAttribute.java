import org.apache.jackrabbit.core.config.ConfigurationException;
import org.apache.jackrabbit.core.config.RepositoryConfigurationParser;

import org.w3c.dom.Element;

class ReplaceVariablesInLongAttribute extends RepositoryConfigurationParser {
  ReplaceVariablesInLongAttribute() {
    super(null);
  }
  
  void pattern(Element element) throws ConfigurationException {
    String value = getAttribute(element, SYNC_DELAY_ATTRIBUTE, DEFAULT_SYNC_DELAY);
    Long.parseLong(replaceVariables(value));
  }
}
