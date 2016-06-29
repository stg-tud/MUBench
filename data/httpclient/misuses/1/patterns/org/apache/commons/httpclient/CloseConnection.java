package org.apache.commons.httpclient;

import java.io.IOException;

class CloseConnection {
  private void executeWithRetry(final HttpMethod method) throws IOException, HttpException {
    try {
        while (true) {
            if (!this.conn.isOpen()) {
                this.conn.open();
                if (this.conn.isProxied() && this.conn.isSecure() 
                && !(method instanceof ConnectMethod)) {
                    if (!executeConnect()) {
                        return;
                    }
                }
            }
            try {
                method.execute(state, this.conn);
                break;
            } catch (HttpRecoverableException httpre) {
                this.conn.close();
            }
        }
    } catch (IOException e) {
        if (this.conn.isOpen()) {
            this.conn.close();
        }
        throw e;
    } catch (RuntimeException e) {
        if (this.conn.isOpen()) {
            this.conn.close();
        }
        throw e;
    }
  }
}
