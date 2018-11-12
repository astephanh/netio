#!/usr/bin/env python

import logging,sys, os, time
import squeezebox
from serial import Serial

Server = 'hp'
Playername = 'Office'
serial_dev = '/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0'
countdown = 180

class Relay():
  def __init__(self,device):
    self.device = device
    try:
      self.ser = Serial(device)
      self.disable()
    except Exception:
      logger.error("Can't open Serial Interface: %s" % device)
      sys.exit(1)

  def enable(self):
    self.ser.write(b'\xA0\x01\x01\xA2')

  def disable(self):
    self.ser.write(b'\xA0\x01\x00\xA1')


if __name__=='__main__':
  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
  logger = logging.getLogger(__name__)

  logger.info("starting")
  relay = Relay(serial_dev)
  amp_active = False
  pl = squeezebox.Player(Server, Playername)
  off_count = 0

  try:
    while True:
      time.sleep(2)
      if pl.is_running():
        off_count = 0
        if not amp_active:
          logger.info("Starting AMP")
          relay.enable()
          amp_active = True
      else:
        if amp_active:
          if off_count < countdown:
            logger.info("sleeping {} von {}".format(off_count,countdown))
            off_count +=1
          else:
            logger.info("Stopping AMP")
            relay.disable()
            amp_active = False

  finally:
    relay.disable()
    pl.destroy()
    exit(0)
