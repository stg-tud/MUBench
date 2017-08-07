import de.strullerbaumann.visualee.examiner.Examiner;
import de.strullerbaumann.visualee.source.entity.JavaSource;
import java.util.Scanner;

abstract class JumpOverJavaToken extends Examiner {
  protected static String jumpOverJavaToken(String token, Scanner scanner) {
    String nextToken = token;
    while (isAJavaToken(nextToken)) {
      if (!scanner.hasNext()) {
        throw new IllegalArgumentException("Insufficient number of tokens to jump over");
      }
      if (nextToken.startsWith("@") && nextToken.indexOf('(') > -1 && !nextToken.endsWith(")")) {
        nextToken = scanAfterClosedParenthesis(nextToken, scanner);
      } else {
        nextToken = scanner.next();
      }
    }
    return nextToken;
  }
}
