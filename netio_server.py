#!/usr/bin/env python3

import logging,sys, os, time
from serial import Serial
from flask import Flask

http_port = 54321
serial_dev = '/dev/ttyUSB0'

class Relay():
  def __init__(self,device):
    self.device = device
    self.active = True
    try:
      self.ser = Serial(device)
    except Exception:
      logger.error("Can't open Serial Interface: %s" % device)
      sys.exit(1)

    # set to false on start
    self.disable()

  def enable(self):
    self.ser.write(b'\xA0\x01\x01\xA2')
    self.active = True

  def disable(self):
    self.ser.write(b'\xA0\x01\x00\xA1')
    self.active = False


if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    @app.route("/AmpON")
    def amp_on():
          relay.enable()
          logger.debug("starting AMP")
          return "activated"

    @app.route("/AmpOFF")
    def amp_off():
          relay.disable()
          logger.debug("Stopping AMP")
          return "disabled"

    @app.route("/")
    def hello():
      return "Status: %s" % relay.active

    try:
      relay = Relay(serial_dev)
      app.run(debug=False, port=http_port)
    finally:
      relay.disable()

