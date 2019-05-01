#!/usr/bin/env python3

import logging
import time
import socket
import subprocess
from threading import Thread, Event, Lock
from urllib.request import urlopen


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
    self.logger.info("WebOSHandler started, TV-IP: {}".format(self.IP))

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
      status = urlopen("http://%s:%i/" % (self.IP,self.PORT), timeout=3).read().rstrip()
      status = status.decode('utf-8')
      if status == 'Hello world':
        if not self.running:
          self.logger.info("TV running")
          self.lock.acquire()
          self.running = True
          self.lock.release()
      else:
        if self.running:
          self.logger.info("TV stopped")
          self.lock.acquire()
          self.running = False
          self.lock.release()
    except Exception as e:
      if self.running:
        self.logger.info("TV stopped")
        self.lock.acquire()
        self.running = False
        self.lock.release()
    except socket.timeout:
      if self.running:
        self.logger.info("TV Timeout")
        self.lock.acquire()
        self.running = False
        self.lock.release()

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
    print('\n\t%s ip_address port\n' % sys.argv[0])
    exit(0)

  ip = sys.argv[1]
  port = sys.argv[2]
  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  logger = logging.getLogger(__name__)
  print('Requested ip address:', ip)

  lg = MyWebOSHandler(ip,port)

  try:
    while True:
      time.sleep(0.2)
  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    logger.info("Stopping ...")
    lg.destroy()

