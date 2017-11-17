#!/usr/bin/env python3

# radio configuration register page
# starting at 0xdf00, 62 bytes

import logging
from binascii import hexlify
from .defs import REGS

if not logging.root.handlers:
    logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(name=__name__)

test = (b'\x0cN\xff@\x00\x00\x00\x0c\x00%\x95U\xca\xa3\x01#\x116\x07\x0f\x18'
        b'\x17l\x03@\x91\xb6\x10\xea*\x00\x1fY??\x881\t\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x00\x11\x03\x00\xff\x80'
        b'\xff\xff\xff\xff')


def nicebits(bits):
    return hexlify(bits).decode('ascii')

R_O = REGS


def br(inbytes):
    return bytes(reversed(inbytes))


class RfcatRadioDescriptor:
    length = 62

    def __init__(self, blob=None):
        self.dirty = True
        self.deserialize(blob or bytearray(self.length))
        # self.dirty = False

    def __eq__(self, other):
        for attrib in self.__slots__:
            if getattr(self, attrib) != getattr(other, attrib):
                return False
        return True

    def deserialize(self, inblob):
        """understand the passed radio configuration minipage"""
        self.sync = br(inblob[R_O.SYNC:R_O.SYNC + 2])
        self.pktlen = inblob[R_O.PKTLEN]
        self.pktctrl = br(inblob[R_O.PKTCTRL:R_O.PKTCTRL + 2])
        self.addr = inblob[R_O.ADDR]
        self.channr = inblob[R_O.CHANNR]
        self.fsctrl = br(inblob[R_O.FSCTRL:R_O.FSCTRL + 2])
        self.freq = br(inblob[R_O.FREQ:R_O.FREQ + 3])
        self.mdmcfg = br(inblob[R_O.MDMCFG:R_O.MDMCFG + 5])
        self.deviatn = inblob[R_O.DEVIATN]
        self.mcsm = br(inblob[R_O.MCSM:R_O.MCSM + 3])
        self.foccfg = inblob[R_O.FOCCFG]
        self.bscfg = inblob[R_O.BSCFG]
        self.agcctrl = br(inblob[R_O.AGCCTRL:R_O.AGCCTRL + 3])
        self.frend = br(inblob[R_O.FREND:R_O.FREND + 2])
        self.fscal = br(inblob[R_O.FSCAL:R_O.FSCAL + 4])
        self.z = (inblob[R_O.Z:R_O.Z + 3] +
                  inblob[R_O.Z_3:R_O.Z_3 + 1] +
                  inblob[R_O.Z_4:R_O.Z_4 + 4])
        self.test = br(inblob[R_O.TEST:R_O.TEST + 3])
        self.pa_table = br(inblob[R_O.PA_TABLE:R_O.PA_TABLE + 8])
        self.iocfg = br(inblob[R_O.IOCFG:R_O.IOCFG + 3])
        self.partnum = inblob[R_O.PARTNUM]
        self.chipid = inblob[R_O.CHIPID]
        self.freqest = inblob[R_O.FREQEST]
        self.lqi = inblob[R_O.LQI]
        self.rssi = inblob[R_O.RSSI]
        self.marcstate = inblob[R_O.MARCSTATE]
        self.pkstatus = inblob[R_O.PKSTATUS]
        self.vco_vc_dac = inblob[R_O.VCO_VC_DAC]

    def serialize(self):
        """return a bytearray representing the whole radio
           configuration minipage, suitable for bulk transfer
           or application-parameter-sharing"""
        outblob = bytearray(self.length)
        outblob[R_O.SYNC:R_O.SYNC + 2] = br(self.sync)
        outblob[R_O.PKTLEN] = self.pktlen
        outblob[R_O.PKTCTRL:R_O.PKTCTRL + 2] = br(self.pktctrl)
        outblob[R_O.ADDR] = self.addr
        outblob[R_O.CHANNR] = self.channr
        outblob[R_O.FSCTRL:R_O.FSCTRL + 2] = br(self.fsctrl)
        outblob[R_O.FREQ:R_O.FREQ + 3] = br(self.freq)
        outblob[R_O.MDMCFG:R_O.MDMCFG + 5] = br(self.mdmcfg)
        outblob[R_O.DEVIATN] = self.deviatn
        outblob[R_O.MCSM:R_O.MCSM + 3] = br(self.mcsm)
        outblob[R_O.FOCCFG] = self.foccfg
        outblob[R_O.BSCFG] = self.bscfg
        outblob[R_O.AGCCTRL:R_O.AGCCTRL + 3] = br(self.agcctrl)
        outblob[R_O.FREND:R_O.FREND + 2] = br(self.frend)
        outblob[R_O.FSCAL:R_O.FSCAL + 4] = br(self.fscal)
        outblob[R_O.Z:R_O.Z + 3] = self.z[0:3]
        outblob[R_O.Z_3] = self.z[3]
        outblob[R_O.Z_4:R_O.Z_4 + 4] = self.z[4:]
        outblob[R_O.TEST:R_O.TEST + 3] = br(self.test)
        outblob[R_O.PA_TABLE:R_O.PA_TABLE + 8] = br(self.pa_table)
        outblob[R_O.IOCFG:R_O.IOCFG + 3] = br(self.iocfg)
        outblob[R_O.PARTNUM] = self.partnum
        outblob[R_O.CHIPID] = self.chipid
        outblob[R_O.FREQEST] = self.freqest
        outblob[R_O.LQI] = self.lqi
        outblob[R_O.RSSI] = self.rssi
        outblob[R_O.MARCSTATE] = self.marcstate
        outblob[R_O.PKSTATUS] = self.pkstatus
        outblob[R_O.VCO_VC_DAC] = self.vco_vc_dac
        return outblob

    def _chip_get_frequency(self):
        log.info("retrieving frequency")
        rcv = self.peek(R_O.BASE + R_O.FREQ, 3)
        log.debug("_chip_get_frequency() -> %s", nicebits(rcv))
        self.freq = br(rcv)

    def _chip_set_frequency(self):
        log.info("setting frequency")
        pokeb = br(self.freq)
        ret = self.poke(R_O.BASE + R_O.FREQ, pokeb)
        log.debug("_chip_set_frequency(%s) -> %s",
                  nicebits(pokeb), nicebits(ret))
        return ret

    @property
    def frequency(self):
        """return the true frequency in float-Hz"""
        # if self.dirty:
        self._chip_get_frequency()
        _freq = (self.freq[0] +
                 (self.freq[1] << 8) +
                 (self.freq[2] << 16)) * 2.4e6 / 2 ** 16
        log.debug("frequency: %f Hz = 0x%s", _freq,
                  hexlify(self.freq).decode('ascii'))
        return _freq
