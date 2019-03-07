package com.sun.javacard.apduio;

public class Apdu {

    public byte[] command;
    public byte[] dataIn;

    public void setLc(int lc) {
        
    }

    public void setLe(int le) {

    }

    public int[] getDataOut() {
        return new int[0];
    }

    public Object getSw1Sw2() {
        return null;
    }
}