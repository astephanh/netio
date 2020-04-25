#!/usr/bin/env python3

import logging
import sys
import os
import time
import signal
import socket
from threading import Thread, Event, Lock
from http.server import BaseHTTPRequestHandler,HTTPServer
from lib import webos, squeezebox, gpio

# rest api
http_server_port = 54321
AmpPin = 11
AmpCounter = 60

#squeezebox settings
Server = 'hp'
PlayerName = 'LivingRoom'

# LG TV
LG_ADRESS = "192.168.123.217"
#LG_ADRESS = "127.0.0.1"
LG_PORT = 3000


if __name__ == '__main__':     # Program start from here

  #logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)
  logger = logging.getLogger(__name__)

  # wait on restart
  if not logging.getLevelName(logger.getEffectiveLevel()) == 'DEBUG':
    logger.info("Waiting 10 seconds to save amp")
    time.sleep(10)

  Amp = gpio.GpioHandler(AmpPin)
  tv = webos.MyWebOSHandler(LG_ADRESS,LG_PORT)
  pl = squeezebox.Player(Server,PlayerName)
  #hs = MyHttpServer()

  def signal_term_handler(signal, frame):
    logger.info("Stopping Threads ...")
    tv.destroy()
    pl.destroy()
    #hs.destroy()
    logger.info("doing GPIO Cleanup")
    Amp.destroy()
    sys.exit(0)

  # register sigterm handler
  signal.signal(signal.SIGTERM, signal_term_handler)

  try:
    counter = 0
    while True:
      # not too fast
      time.sleep(2)

      # make sure amp turnes off if nothing plays
      if not (pl.running or tv.running) and Amp.running:
        if counter >= AmpCounter:
          logger.info("Counter limit hit, Stopping Amp")
          Amp.stop()
          counter = 0
        else:
          logger.debug("Countdown {}".format(counter))
          counter +=1
        continue
      else:
        # reset counter
        if counter > 0:
          logger.info("Counter reset")
          counter = 0

      if tv.running:
        Amp.start()
        if pl.running:
          pl.stop()

      if pl.running:
        Amp.start()


  except KeyboardInterrupt:
    # stop all threads
    signal_term_handler(None, None)


