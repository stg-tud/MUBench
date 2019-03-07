package org.apache.commons.httpclient;

import java.io.IOException;

class CloseConnection {
  void pattern(HttpConnection conn, HttpMethod method, HttpState state) throws IOException, HttpException {
    try {
        while (true) {
            if (!conn.isOpen()) {
                conn.open();
                if (conn.isProxied() && conn.isSecure() && !(method instanceof ConnectMethod)) {
                    // initialize connect method...
                }
            }
            try {
                method.execute(state, conn);
                break;
            } catch (HttpRecoverableException httpre) {
                conn.close();
            }
        }
    } catch (IOException e) {
        if (conn.isOpen()) {
            conn.close();
        }
        throw e;
    } catch (RuntimeException e) {
        if (conn.isOpen()) {
            conn.close();
        }
        throw e;
    }
  }
}
