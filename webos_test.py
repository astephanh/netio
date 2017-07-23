#!/usr/bin/env python


import RPi.GPIO as GPIO
import logging,sys, os
import time
import socket
from threading import Thread, Event, Lock
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

import urllib2
import subprocess

LG_ADRESS="192.168.123.217"
LG_PORT=9080

class MyWebOSHandler:
  def __init__(self,ip,logger=None):
    """ checking TV for Status """
    self.logger = logger or logging.getLogger(__name__)
    self.IP = ip
    self.up = False
    self.running = False
    self.PORT = LG_PORT

    self.t_stop = Event()
    self.t = Thread(target=self.watch_tv, args=(1, self.t_stop))
    self.t.start()
    self.logger.info("WebOSHandler started, TV-IP: %s" % LG_ADRESS)

  def _ping_ip(self):
    retcode = subprocess.call("ping" + " -c1 -w2 %s >/dev/null" % self.IP, shell=True)
    if(retcode == 0):
      self.logger.debug("IP Adress up: %s" % self.IP)
      self.up = True
      self._check_if_running()
    else:
      self.logger.debug("IP Adress down")
      self.up = False
      self.running = False

  def _check_if_running(self):
    """ check if tv is running """
    try:
      status = urllib2.urlopen("http://%s:%i/" % (self.IP,self.PORT), timeout=2).read() 
      if status.split("=")[1] == 'ok':
        self.logger.debug("TV running")
        self.running = True
      else:
        self.logger.debug("TV stopped")
        self.running = False
    except urllib2.URLError, e:
      self.logger.debug("TV not ready")

  def is_running(self):
    """ return True if TV is up and running """
    return self.running

  def watch_tv(self, arg1, stop_event):
    while(not stop_event.is_set()):
      self._ping_ip()
      time.sleep(2)

  def destroy(self):
      self.t_stop.set()
      self.logger.debug("WebOSHandler Thread stopped")


if __name__ == '__main__':     # Program start from here

  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  logger = logging.getLogger(__name__)

  lg = MyWebOSHandler(LG_ADRESS)

  try:
    while True:
      time.sleep(0.2)
  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    logger.info("Stopping ...")
    lg.destroy()

