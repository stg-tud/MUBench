import org.apache.jackrabbit.core.config.ConfigurationException;
import org.apache.jackrabbit.core.config.RepositoryConfigurationParser;

import org.w3c.dom.Element;

class ReplaceVariablesInStringAttribute extends RepositoryConfigurationParser {
  ReplaceVariablesInStringAttribute() {
    super(null);
  }
  
  void pattern(Element element) throws ConfigurationException {
    String value = getAttribute(element, ID_ATTRIBUTE, null);
    replaceVariables(value);
  }
}
