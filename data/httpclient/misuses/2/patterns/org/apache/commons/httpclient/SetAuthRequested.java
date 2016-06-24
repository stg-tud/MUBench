import org.apache.commons.httpclient.auth.AuthState;
import org.apache.commons.httpclient.auth.AuthenticationException;

class SetAuthRequested {
  AuthState pattern(HttpMethod method) throws AuthenticationException {
    AuthState authstate = method.getHostAuthState();
    if (authstate.isPreemptive()) {
      authstate.invalidate();
      authstate.setAuthRequested(true);
    }
    return authstate;
  }
}
