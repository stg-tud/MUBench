import org.apache.jackrabbit.core.config.ConfigurationException;
import org.apache.jackrabbit.core.config.RepositoryConfigurationParser:

class ReplaceVariablesInAttribute extends RepositoryConfigurationParser {
  String pattern(Element element) throws ConfigurationException {
    String value = getAttribute(element, ID_ATTRIBUTE, null);
    return replaceVariables(value);
  }
}