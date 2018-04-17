#!/usr/bin/env python

import logging,sys, os, time
import squeezebox
from serial import Serial

Server = 'hp'
Playername = 'Office'
serial_dev = '/dev/ttyUSB0'

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

  try:
    off_count = 0
    while True:
      time.sleep(2)
      if pl.is_running():
        if not amp_active:
          logger.info("Starting AMP")
          off_count = 0
          relay.enable()
          amp_active = True
      else:
        if amp_active and off_count == 3:
          logger.info("Stopping AMP")
          relay.disable()
          amp_active = False
        else:
          off_count +=1

  finally:
    relay.disable()
    pl.destroy()
    exit(0)
