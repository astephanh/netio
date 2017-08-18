#!/usr/bin/env python


import RPi.GPIO as GPIO
import logging,sys, os
import time
import signal
import socket
import urllib2
from threading import Thread, Event, Lock
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import webos
import squeezebox

# rest api
http_server_port = 54321
AmpPin = 11

#squeezebox settings
Server = 'hp'
PlayerName = 'LivingRoom'

# LG TV
LG_ADRESS = "192.168.123.217"
LG_PORT = 3000


class MyHttpHandler(BaseHTTPRequestHandler):
    def __init__(self,  *args):
      """ change Player for encoder """
      self.logger = logger or logging.getLogger(__name__)
      BaseHTTPRequestHandler.__init__(self, *args)
      self.running = False

    def log_message(self, format, *args):
      return

    #Handler for the GET requests
    def do_GET(self):
        # do something with uri
        self.logger.info("GOT URL: %s" %  self.path)
        try:
            if self.path == "/AmpON":
                self.logger.info("Starting AMP")
                GPIO.output(AmpPin, GPIO.HIGH)
                self._return_200()
            elif self.path == "/AmpOFF":
                self.logger.info("Stopping AMP")
                GPIO.output(AmpPin, GPIO.LOW)
                self._return_200()
            else:
                return self._return_404()
        except ValueError:
            pass

    def _return_200(self):
        self.logger.debug("Responding 200")
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write("ok\n")

    def _return_404(self):
        self.logger.debug("Responding 404")
        self.send_response(404)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write("URL %s not found\n" % self.path)

class HTTPServerV6(HTTPServer):
  address_family = socket.AF_INET6

class MyHttpServer:
    """ HTTP Server for changing the active player """

    def __init__(self,logger=None):
        self.logger = logger or logging.getLogger(__name__)

        # start http server for Jive remote
        self.t = Thread(target=self._select_player, args=())
        self.t.start()

    def _select_player(self):
        """ Waits on http for the active player """

        self.http_server = HTTPServerV6(('::', http_server_port), MyHttpHandler)
        self.logger.info('Http Server started on port %i' % http_server_port)

        #Wait forever for incoming http requests
        self.logger.debug("HTTP Server Thread started")
        try:
            self.http_server.serve_forever()
        except Exception as e:
            self.logger.debug("Http Server closed")
            pass

    def AmpOn(self):
      self.logger.debug(dir(self.http_server))

    def AmpOff(self):
      self.logger.debug(dir(self.http_server))

    def destroy(self):
        self.http_server.socket.close()


if __name__ == '__main__':     # Program start from here

  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  logger = logging.getLogger(__name__)
  tv_was_running = False
  pl_was_running = False

  GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
  GPIO.setup(AmpPin, GPIO.OUT)
  GPIO.output(AmpPin, GPIO.LOW)
  logger.debug("Init Pin %i" % AmpPin)

  # wait on restart 
  logger.info("Waiting 10 seconds to save amp")
  time.sleep(10)

  lg = webos.MyWebOSHandler(LG_ADRESS,LG_PORT)
  pl = squeezebox.Player(Server,PlayerName)
  hs = MyHttpServer()

  def signal_term_handler(signal, frame):
    logger.info("Stopping Threads ...")
    lg.destroy()
    pl.destroy()
    hs.destroy()
    logger.info("doing GPIO Cleanup")
    GPIO.cleanup()
    sys.exit(0)

  # register sigterm handler
  signal.signal(signal.SIGTERM, signal_term_handler)

  try:
    while True:
      time.sleep(2)
      # if tv is turned on, stop player
      if lg.is_running():
        if not tv_was_running:
          logger.info("TV Turned ON")
          GPIO.output(AmpPin, GPIO.HIGH)
          if pl.running:
            pl.stop()
          tv_was_running = True
          pl_was_running = False
        else:
          # make sure player ist turned off
          if pl.running:
            pl.stop()
      else:
        if tv_was_running:
          logger.info("TV Turned OFF")
          GPIO.output(AmpPin, GPIO.LOW)
          tv_was_running = False
        else:
          # turn amp on if player is running
          if pl.running and not pl_was_running:
            logger.info("Player %s running, Turning Amp ON" % PlayerName)
            GPIO.output(AmpPin, GPIO.HIGH)
            pl_was_running = True

  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    signal_term_handler()


