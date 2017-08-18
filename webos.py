#!/usr/bin/env python


import logging
import time
import socket
from threading import Thread, Event, Lock

import urllib2
import subprocess


class MyWebOSHandler:
  def __init__(self,ip,port,logger=None):
    """ checking TV for Status """
    self.logger = logger or logging.getLogger(__name__)
    self.IP = ip
    self.PORT = int(port)
    self.running = False

    self.t_stop = Event()
    self.lock = Lock()
    self.t = Thread(target=self.watch_tv, args=(1, self.t_stop))
    self.t.start()
    self.logger.info("WebOSHandler started, TV-IP: %s" % self.IP)

  def _ping_ip(self):
    retcode = subprocess.call("ping" + " -c1 -w2 %s >/dev/null" % self.IP, shell=True)
    if(retcode == 0):
      self._check_if_running()
    else:
      self.logger.debug("TV offline")
      self.lock.acquire()
      self.running = False
      self.lock.release()

  def _check_if_running(self):
    """ check if tv is running """
    try:
      status = urllib2.urlopen("http://%s:%i/" % (self.IP,self.PORT), timeout=3).read().rstrip()
      if status == 'Hello world':
        self.logger.debug("TV running")
        self.lock.acquire()
        self.running = True
        self.lock.release()
      else:
        self.logger.debug("TV stopped (status: %s)" % status)
        self.lock.acquire()
        self.running = False
        self.lock.release()
    except urllib2.URLError, e:
      self.logger.debug("TV not ready %s" % e)
      self.lock.acquire()
      self.running = False
      self.lock.release()
    except socket.timeout:
      self.logger.debug("TV Timeout")

  def is_running(self):
    """ return True if TV is running """
    return self.running

  def watch_tv(self, arg1, stop_event):
    while(not stop_event.is_set()):
      self._ping_ip()
      time.sleep(2)

  def destroy(self):
      self.t_stop.set()
      self.logger.debug("WebOSHandler Thread stopped")


if __name__ == '__main__':     # Program start from here

  import sys

  if len(sys.argv) < 3:
    print '\n\t%s ip_address port\n' % sys.argv[0]
    exit(0)

  ip = sys.argv[1]
  port = sys.argv[2]
  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  logger = logging.getLogger(__name__)
  print 'Requested ip address:', ip

  lg = MyWebOSHandler(ip,port)

  try:
    while True:
      time.sleep(0.2)
  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    logger.info("Stopping ...")
    lg.destroy()

