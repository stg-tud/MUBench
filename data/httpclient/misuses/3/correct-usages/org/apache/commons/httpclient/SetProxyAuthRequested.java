package org.apache.commons.httpclient;

import org.apache.commons.httpclient.auth.AuthState;
import org.apache.commons.httpclient.auth.AuthenticationException;

class SetProxyAuthRequested {
  void pattern(HttpMethod method) throws AuthenticationException {
    AuthState authstate = method.getProxyAuthState();
    if (authstate.isPreemptive()) {
      authstate.invalidate();
      authstate.setAuthRequested(true);
    }
  }
}
