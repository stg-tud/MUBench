package com.linuxnet.jpcsc;

public class Card {
    public void BeginTransaction() {

    }

    public byte[] Transmit(byte[] capdu, int i, int length) {
        return new byte[0];
    }

    public void EndTransaction(PCSC resetCard) {

    }

    public void Disconnect() {

    }
}
