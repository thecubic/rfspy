# rfspy
python driver for rfspy devices

## Platforms

Tested on Linux so far, anything that `pyusb` works on should be fine

## Feature support

Pretty much just ping and report the frequency.

## Testing

so far only a `rfspy-ping-all`, that will enumerate all USB devices it can find
and run a ping on each, reporting output.

### Example

```
$ rfspy-ping-all
dongle: <MutableRfcat Great Scott Gadgets : YARD Stick One @ USB 3:3 enumerated>
build: YARDSTICKONE r0348
ping: True

dongle: <MutableRfcat Great Scott Gadgets : YARD Stick One @ USB 3:4 enumerated>
build: YARDSTICKONE r0348
ping: True

dongle: <MutableRfcat Great Scott Gadgets : YARD Stick One @ USB 3:5 enumerated>
build: YARDSTICKONE r0348
ping: True

dongle: <MutableRfcat RfCat : Dons Dongle @ USB 3:7 enumerated>
build: DONSDONGLE r0340
ping: True

dongle: <MutableRfcat ComThings : PandwaRF Dongle @ USB 3:25 enumerated>
build: GollumRfBigCCtl
ping: True
```
