import java.io.IOException;

import org.mozilla.javascript.FunctionNode;
import org.mozilla.javascript.IRFactory;
import org.mozilla.javascript.Node;
import org.mozilla.javascript.Token;

class CallInitOnce {
  Node pattern(IRFactory nf, int functionType, Node memberExprNode, int functionIndex, String name, Node body) throws IOException {
    int baseLineno = ts.getLineno();
    
    FunctionNode fnNode = nf.createFunction(name);
    // configure fnNode...

    Node pn = nf.initFunction(fnNode, functionIndex, body, functionType);
    if (memberExprNode != null) {
      pn = nf.createAssignment(Token.ASSIGN, memberExprNode, pn);
      if (functionType != FunctionNode.FUNCTION_EXPRESSION) {
        pn = nf.createExprStatementNoReturn(pn, baseLineno);
      }
    }
    return pn;
  }
}