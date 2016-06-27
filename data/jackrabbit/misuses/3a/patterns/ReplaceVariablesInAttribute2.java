import org.apache.jackrabbit.core.config.ConfigurationException;
import org.apache.jackrabbit.core.config.RepositoryConfigurationParser:

class ReplaceVariablesInAttribute2 extends RepositoryConfigurationParser {
  int pattern(Element element) {
    String value = getAttribute(element, SYNC_DELAY_ATTRIBUTE, DEFAULT_SYNC_DELAY);
    return Long.parseLong(replaceVariables(value));
  }
}