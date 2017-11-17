#!/usr/bin/env python3


class REGS:
    BASE = 0xdf00
    # Sync Word
    SYNC = 0x00
    # Packet length
    PKTLEN = 0x02
    # Packet automation control
    PKTCTRL = 0x03
    # Device Address
    ADDR = 0x05
    # Channel Number
    CHANNR = 0x06
    # Frequency Synthesizer Control
    FSCTRL = 0x07
    # Freqency Control
    FREQ = 0x09
    # Modem Configuration
    MDMCFG = 0x0c
    # Modem Deviation
    DEVIATN = 0x11
    # Main Radio Control State Machine Configuration
    MCSM = 0x12
    # Frequency Offset Compensation
    FOCCFG = 0x15
    # Bit Synchronization
    BSCFG = 0x16
    # AGC Control
    AGCCTRL = 0x17
    # Front End RX
    FREND = 0x1a
    # Frequency Synthesizer Calibration
    FSCAL = 0x1c
    Z = 0x20
    TEST = 0x23
    Z_3 = 0x26
    # Power Amplifier output settings
    PA_TABLE = 0x27
    IOCFG = 0x2f
    Z_4 = 0x32
    PARTNUM = 0x36
    CHIPID = 0x37
    FREQEST = 0x38
    LQI = 0x39
    RSSI = 0x3a
    MARCSTATE = 0x3b
    PKSTATUS = 0x3c
    VCO_VC_DAC = 0x3d


class USB:
    MAX_BLOCK_SIZE = 512
    RX_WAIT = 1000
    TX_WAIT = 10000

    class BM:
        class REQTYPE:
            TGTMASK = 0x1f
            TGT_DEV = 0x00
            TGT_INTF = 0x01
            TGT_EP = 0x02

            TYPEMASK = 0x60
            TYPE_STD = 0x00
            TYPE_CLASS = 0x20
            TYPE_VENDOR = 0x40
            TYPE_RESERVED = 0x60

            DIRMASK = 0x80
            DIR_OUT = 0x00
            DIR_IN = 0x80

    GET_STATUS = 0x00
    CLEAR_FEATURE = 0x01
    SET_FEATURE = 0x03
    SET_ADDRESS = 0x05
    GET_DESCRIPTOR = 0x06
    SET_DESCRIPTOR = 0x07
    GET_CONFIGURATION = 0x08
    SET_CONFIGURATION = 0x09
    GET_INTERFACE = 0x0a
    SET_INTERFACE = 0x11
    SYNCH_FRAME = 0x12


class APP:
    GENERIC = 0x01
    DEBUG = 0xfe
    SYSTEM = 0xff


class SYS:
    class CMD:
        PEEK = 0x80
        POKE = 0x81
        PING = 0x82
        STATUS = 0x83
        POKE_REG = 0x84
        GET_CLOCK = 0x85
        BUILDTYPE = 0x86
        BOOTLOADER = 0x87
        RFMODE = 0x88
        COMPILER = 0x89
        PARTNUM = 0x8e
        RESET = 0x8f
        CLEAR_CODES = 0x90


class EP0:
    class CMD:
        GET_DEBUG_CODES = 0x00
        GET_ADDRESS = 0x01
        POKEX = 0x01
        PEEKX = 0x02
        PING0 = 0x03
        PING1 = 0x04
        RESET = 0xfe


class DEBUG:
    class CMD:
        STRING = 0xf0
        HEX = 0xf1
        HEX16 = 0xf2
        HEX32 = 0xf3
        INT = 0xf4


class EP5:
    class OUT:
        MAX_PACKET_SIZE = 64
        BUFFER_SIZE = 516

    class IN:
        MAX_PACKET_SIZE = 64


class LC:
    class USB:
        INITUSB = 0x2
        DATA_RESET_RESUME = 0xa
        RESET = 0xb
        EP5OUT = 0xc

    class RF:
        VECTOR = 0x10

    class RFTXRX:
        VECTOR = 0x11

    class MAIN:
        RFIF = 0xd


class LCE:
    class USB:
        class EP0:
            SENT_STALL = 0x4

        class EP5:
            TX_WHILE_INBUF_WRITTEN = 0x1
            OUT_WHILE_OUTBUF_WRITTEN = 0x5
            LEN_TOO_BIG = 0x6
            GOT_CRAP = 0x7
            STALL = 0x8
        DATA_LEFTOVER_FLAGS = 0x9

    class RF:
        RXOVF = 0x10
        RX_TXUNF = 0x11
