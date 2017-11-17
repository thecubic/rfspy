#!/usr/bin/env python3

import usb
import usb.core
from operator import attrgetter
import logging
import time
import struct
import random
from binascii import hexlify
import array
import traceback
from .defs import APP, SYS

lvl = logging.INFO

if not logging.root.handlers:
    logging.basicConfig(level=lvl)

log = logging.getLogger(name=__name__)


def nicebits(bits):
    return hexlify(bits).decode('ascii')


class RfcatUSB:
    "temporary, tightly-usb-integrated Rfcat driver"
    reset_tries = 5
    device = None
    manufacturer = None
    product = None
    bus = None
    address = None
    state = 'uninitialized'

    def __init__(
        self,
        device,
        reset_on_exit=False
    ):
        self.device = device
        self.get_info()
        self.reset_on_exit = reset_on_exit

    def show(self):
        print(self.device)

    def get_info(self, resets=None):
        """get information once"""
        if resets is None:
            resets = self.reset_tries
        try:
            self.manufacturer = self.device.manufacturer
            self.product = self.device.product
            self.bus = self.device.bus
            self.address = self.device.address
            self.configuration = self.device[0]
            self.interface = self.configuration[(0, 0)]
            for endpoint in self.interface:
                direction = usb.util.endpoint_direction(
                    endpoint.bEndpointAddress)
                if direction == usb.util.ENDPOINT_IN:
                    # device-to-host / read
                    self.readEp = endpoint
                elif direction == usb.util.ENDPOINT_OUT:
                    # host-to-device / write
                    self.writeEp = endpoint
            # take 5 bytes away for resp(1), app(1), cmd(1), buflen(2)
            self.max_payload = (min((self.readEp.wMaxPacketSize,
                                     self.writeEp.wMaxPacketSize))
                                - 5)
            self.state = 'enumerated'
        except Exception:
            if resets:
                log.error("USB problem, attempting reset")
                self.device.reset()
                self.get_info(resets=resets - 1)
            else:
                raise

    def open(self):
        try:
            self.device.get_active_configuration()
            log.debug("configuration was already set")
        except usb.core.USBError:
            log.debug("need to set configuration")
            # likely unset configuration
            # we only have one configuration, but are required to set it
            self.device.set_configuration()
        self.state = 'initialized'

    def close(self, force_reset=False):
        if self.reset_on_exit or force_reset:
            self.reset()
        self.state = 'closed'

    def write_rpc(self, app, cmd, buf=None):
        if buf is None:
            buf = b''
        payload = struct.pack("<BBH", app, cmd, len(buf)) + buf
        sent = self.writeEp.write(payload)
        return (len(payload), sent)

    def read_rpc(self, app, cmd, amt):
        payload = self.readEp.read(amt)
        return payload

    def rpc_sym(self, app, cmd, buf):
        payloadsz, writtensz = self.write_rpc(app, cmd, buf)
        log.debug("attempted %d, wrote %d", payloadsz, writtensz)
        # extra byte for free yo
        readsz = payloadsz + 1
        payload = self.read_rpc(app, cmd, readsz)
        if payload[1] != app:
            log.warning("application mismatch; got %x, expecting %x",
                        payload[1], app)
        if payload[2] != cmd:
            log.warning("command mismatch; got %x, expecting %x",
                        payload[2], app)
        buflen = struct.unpack("<H", bytes(payload[3:5]))[0]
        buf = bytes(payload[5:])
        if buflen != len(buf):
            log.warning("return size mismatch; read %d embedlen %d",
                        len(buf), buflen)
        return buf

    def rpc(self, app, cmd, buf=None):
        payloadsz, writtensz = self.write_rpc(app, cmd, buf)
        rapp, rcmd, rbuflen, rbuf = self.read_drain()
        if rapp != app:
            log.warning("rpc app mismatch: called %x, returned %x:",
                        app, rapp)
        if rcmd != cmd:
            log.warning("rpc cmd mismatch: called %x, returned %x:",
                        cmd, rcmd)
        return rbuf

    def read_drain(self):
        rbuf = array.array('B', (0,) * self.readEp.wMaxPacketSize)
        rsz = self.readEp.read(rbuf)
        app = rbuf[1]
        cmd = rbuf[2]
        buflen = rbuf[3:5]
        buflen = struct.unpack("<H", bytes(buflen))[0]
        buf = bytes(rbuf[5:rsz])
        if buflen - 5 > self.readEp.wMaxPacketSize:
            r2sz = self.readEp.read(rbuf)
            print(r2sz, rbuf)
        return (app, cmd, buflen, buf)

    def ping_util(
        self,
        buf=None,
        times=1,
        interval=0,
    ):
        """ping utility function"""
        if not times:
            while self.ping(buf=buf):
                time.sleep(interval)
            return False
        else:
            for _ in range(times):
                if not self.ping(buf=buf):
                    return False
                if times != 1:
                    time.sleep(interval)
            return True

    def ping(self, buf=None):
        """ping command"""
        if buf is None:
            sendbuf = bytes([random.randint(0, 255)
                             for _ in range(self.max_payload)])
        else:
            sendbuf = buf
        log.debug("ping with 0x%s", hexlify(sendbuf).decode('ascii'))
        result = self.rpc_sym(APP.SYSTEM, SYS.CMD.PING, sendbuf)
        if result == sendbuf:
            log.debug("pong okay")
        else:
            log.error("ping failed!")
            log.debug("expected %s, recv'd 0x%s",
                      nicebits(sendbuf),
                      nicebits(result))
        return result == sendbuf

    def peek(self, addr, bytecount=1):
        bbuf = self.rpc(APP.SYSTEM, SYS.CMD.PEEK,
                        struct.pack("<HH", bytecount, addr))
        return bbuf

    def poke(self, addr, data):
        # TODO: size checking and such
        ret = self.rpc(APP.SYSTEM, SYS.CMD.POKE,
                       struct.pack("<H", addr) + data)
        return ret

    def reset(self):
        log.warning("resetting device")
        return self.device.reset()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, exc_tb)
            if exc_type is usb.core.USBError:
                self.close(force_reset=True)
            else:
                self.close()
        else:
            self.close()

    @property
    def aes_mode(self):
        """encryption coprocessor mode
           possible states:
            IN/OUT=OFF: sleep
            IN=encrypt, OUT=decrypt
                I distrust RF
            OUT=decrypt, IN=encrypt
                I distrust my connection to the transciever, but trust RF

        """
        pass

    @property
    def amplifier(self):
        "discrete amplifier"
        pass

    @property
    def packet_address(self):
        ""
        # TODO: peek

    def get_radioconfig(self):
        """retrieves the radio configuration minipage"""
        base = 0xdf00
        page_size = 0x3e
        # firmware could someday shrink this
        # but probably not, so tautology
        if page_size > self.max_payload:
            reqs = [(base, self.max_payload),
                    (base + self.max_payload,
                     page_size - self.max_payload)]
        else:
            reqs = [(base, page_size)]
        bbuf = b''
        for addr, amt in reqs:
            bbuf += self.peek(addr, amt)
        return bbuf

    def get_buildinfo(self):
        """retrieves the build information (null-terminated)"""
        bbuf = self.rpc(APP.SYSTEM, SYS.CMD.BUILDTYPE)
        return bbuf.rstrip(b'\x00').decode('ascii')


    def __repr__(self):
        return "<%s %s : %s @ USB %d:%d %s>" % (
            type(self).__name__,
            self.manufacturer,
            self.product,
            self.bus,
            self.address,
            self.state,
        )


class RfcatManager:
    @staticmethod
    def is_usb_rfcat(dev):
        if dev.idVendor == 0x0451 and dev.idProduct == 0x4715:
            # TI USB classic
            return True
        if dev.idVendor == 0x1d50 and dev.idProduct in (0x6047, 0x6048,
                                                        0x605b, 0x60ff):
            # OpenMoko-vendor, not in bootloader mode
            return True
        return False

    @staticmethod
    def find_usb_rfcats(custom_match=None):
        if custom_match is None:
            custom_match = RfcatManager.is_usb_rfcat
            return list(usb.core.find(find_all=True,
                                      custom_match=custom_match))

    def __init__(self, usbdongles=None, factory=RfcatUSB):
        self.usbdongles = usbdongles or []
        self.factory = factory
        self.enumerate()

    def enumerate(self):
        _usbdongles = self.find_usb_rfcats()
        # sorted by usb address
        self.usbdongles = sorted(_usbdongles, key=attrgetter('address'))

    def get_index(self, idx):
        if len(self.usbdongles) > idx:
            return self.usbdongles[idx]
        else:
            raise RuntimeError("index %d unavailable" % idx)

    def get_bus_address(self, bus, address):
        for usbdongle in self.usbdongles:
            if usbdongle.bus == bus and usbdongle.address == address:
                return usbdongle
        raise RuntimeError("bus %d address %d unavailable" % (bus, address))

    def all_devices(self):
        for dongle in self.usbdongles:
            yield dongle

    def all_dongles(self):
        for device in self.all_devices():
            yield self.factory(device)
