package com.sun.javacard.apduio;

import java.io.IOException;

public class CadClientInterface {

    public void powerUp() throws CadTransportException {

    }

    public void exchangeApdu(Apdu theirApdu) throws CadTransportException, IOException {

    }

    public void powerDown(boolean b) throws Exception {

    }
}