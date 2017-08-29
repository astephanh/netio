#!/usr/bin/env python

import time
import logging
from threading import Thread, Event, Lock

import json
import socket
import urllib2


class Player:
  def __init__(self,server,player,logger=None):
    self.logger = logger or logging.getLogger(__name__)
    self.url = 'http://%s:9000/jsonrpc.js' % server
    self.server = server
    self.player = player
    self.playerid = None
    self.squeeze_running = False
    self.running = False


    self.t_stop = Event()
    self.lock = Lock()

    self.header = {
          'Content-Type': 'application/json',
          'User-Agent': 'tpi',
          'Accept': 'application/json',
      }

    self.t = Thread(target=self._watch_player, args=(1, self.t_stop))
    self.t.start()
    self.logger.debug("Server URL: %s" % self.url)
    self.logger.info("SqueezeBoxHandler started, Server: %s, PlayerName: %s" % (self.server,self.player))


  def _watch_player(self, arg1, stop_event):
    while(not stop_event.is_set()):
      self._check_if_squeeze_running()
      if self.squeeze_running:
        self._get_player_id()
        self._check_if_player_running()
      time.sleep(3)

  def _check_if_squeeze_running(self):
    """ test if squeezebox server is up """
    if self.js_request_server(["",["serverstatus",0,999]]):
      self.logger.debug("Squeeze Server STATUS up")
      if not self.squeeze_running:
        self.lock.acquire()
        self.squeeze_running = True
        self.lock.release()
        self.logger.info('Squeeze Server Turned on')
    else:
      self.logger.debug("Squeeze Server STATUS down")
      if self.squeeze_running:
        self.lock.acquire()
        self.squeeze_running = False
        self.playerid = None
        self.lock.release()
        self.logger.info('Squeeze Server Turned off')

  def _get_player_id(self):
    if not self.playerid:
      try:
        response =  self.js_request_server(["",["serverstatus",0,999]])
        for player in response['result']['players_loop']:
          self.logger.debug("found player: %s" % player['name'])
          if player['name'] == self.player:
            self.lock.acquire()
            self.playerid = player['playerid']
            self.lock.release()
            self.logger.info("Player %s has ID: %s" % (self.player,self.playerid))
      except Exception, e:
        self.logger.debug("Squeeze Server Request failed: %s" % e)

      return self.playerid


  def _check_if_player_running(self):
    if self.playerid:
      try:
        mode = self.js_request_player(["mode","?"])['result']['_mode']
        if mode == 'stop' or mode == "pause":
          if self.running:
            self.logger.info("Player stopped")
            self.running = False
          self.logger.debug("Player stopped")
        else:
          if not self.running:
            self.logger.info("Player started")
            self.running = True
          self.logger.debug("Player running")
      except Exception, e:
        self.logger.debug("Squeeze Player Request failed: %s" % e)
    else:
      self.logger.debug("Player not found")
      self.running = False

  def js_request_player(self,params):
      json_string = {
              "id": 1,
              "method": "slim.request",
              "params": [self.playerid, params],
      }

      # craft the request for a url
      req = urllib2.Request(self.url, json.dumps(json_string), headers=self.header)
      try:
        # send the request
        res = urllib2.urlopen(req)
        return  json.loads(res.read())
      except urllib2.URLError, e:
        self.logger.debug("SqueezeBox Error: %s" % e)
        return False
      except Exception:
        self.logger.debug("SqueezeBox Timeout")
        return False

  def js_request_server(self,params):
      json_string = {
              "id": 1,
              "method": "slim.request",
              "params": params,
      }

      # craft the request for a url
      req = urllib2.Request(self.url, json.dumps(json_string), headers=self.header)
      try:
        # send the request
        res = urllib2.urlopen(req)
        return  json.loads(res.read())
      except urllib2.URLError, e:
        self.logger.debug("SqueezeBox Error: %s" % e)
        return False
      except Exception:
        self.logger.debug("SqueezeBox Timeout")
        return False

  def is_running(self):
      return self.running

  def stop(self):
    """ stop if playing """
    if self.is_running():
      resp = self.js_request_player(['stop'])
      self.logger.debug("Player stop: %s" % resp)

  def destroy(self):
    self.t_stop.set()
    self.logger.debug("SqueezeBoxHandler stopped")


if __name__ == "__main__":
  import sys

  if len(sys.argv) < 3:
    print '\n\t%s squeezeboxserver playername\n' % sys.argv[0]
    exit(0)

  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  logger = logging.getLogger(__name__)
  box = Player(sys.argv[1], sys.argv[2],logger)

  try:
    while True:
      time.sleep(0.2)
  except KeyboardInterrupt:
    logger.info("Stopping ...")
    box.destroy()
