package com.sun.javacard.apduio;

import java.io.InputStream;
import java.io.OutputStream;

public enum CadDevice {
    PROTOCOL_T1;

    public static CadClientInterface getCadClientInstance(CadDevice protocolT1, InputStream is, OutputStream os) {
        return null;
    }
}