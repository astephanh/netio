#!/usr/bin/env python3

import time
import logging
from threading import Thread, Event, Lock

import json
import socket
from  urllib.request import Request, urlopen


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

    self.t = Thread(target=self._watch_player, args=(1, self.t_stop))
    self.t.start()
    self.logger.debug("Server URL: {}".format(self.url))
    self.logger.info("SBHandler started, Server: {}, PlayerName: {}".format(
      self.server,self.player))


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
      self.logger.debug("SB Server STATUS up")
      if not self.squeeze_running:
        self.lock.acquire()
        self.squeeze_running = True
        self.lock.release()
        self.logger.info('SB Server ist running')
    else:
      self.logger.debug("SB Server STATUS down")
      if self.squeeze_running:
        self.lock.acquire()
        self.squeeze_running = False
        self.playerid = None
        self.lock.release()
        self.logger.info('SB Server Turned off')

  def _get_player_id(self):
    if not self.playerid:
      try:
        response =  self.js_request_server(["",["serverstatus",0,999]])
        for player in response['result']['players_loop']:
          self.logger.debug("found player: {}".format(player['name']))
          if player['name'] == self.player:
            self.lock.acquire()
            self.playerid = player['playerid']
            self.lock.release()
            self.logger.info("Player {} has ID: {}" .format(self.player,self.playerid))
      except Exception as e:
        self.logger.debug("SB Server Request failed: {}".format(e))

      return self.playerid


  def _check_if_player_running(self):
    if self.playerid:
      try:
        mode = self.js_request_player(["mode","?"])['result']['_mode']
        self.logger.debug("MODE: {}".format(mode))
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
      except Exception as e:
        self.logger.debug("Squeeze Player Request failed: {}".format(e))
    else:
      self.logger.debug("Player not found")
      self.running = False

  def js_request_player(self,params):

      body = {
              "id": 1,
              "method": "slim.request",
              "params": [self.playerid, params],
      }

      # craft the request for a url
      req = Request(self.url)
      req.add_header('Content-Type', 'application/json; charset=utf-8')
      jsondata = json.dumps(body)
      jsondata_as_bytes = jsondata.encode('utf-8')
      req.add_header('Content-Length', len(jsondata_as_bytes))
      self.logger.debug("Post Payload: {}".format(jsondata_as_bytes))
      try:
        # send the request
        resp = urlopen(req,jsondata_as_bytes)
        resp_body = resp.read().decode('utf-8')
        self.logger.debug("REsponse: {}".format(resp_body))
        return  json.loads(resp_body)
      except Exception as e:
        self.logger.debug("SBPlayer Error: {}".format(e))
        return False
      except Exception:
        self.logger.debug("SqueezeBox Timeout")
        return False

  def js_request_server(self,params):
      body = {
              "id": 1,
              "method": "slim.request",
              "params": params,
      }

      # craft the request for a url
      #req = Request(self.url, json.dumps(json_string), headers=self.header)
      req = Request(self.url)
      req.add_header('Content-Type', 'application/json; charset=utf-8')
      jsondata = json.dumps(body)
      jsondata_as_bytes = jsondata.encode('utf-8')
      req.add_header('Content-Length', len(jsondata_as_bytes))
      self.logger.debug("Post Payload: {}".format(jsondata_as_bytes))
      try:
        # send the request
        resp = urlopen(req,jsondata_as_bytes)
        resp_body = resp.read().decode('utf-8')
        return  json.loads(resp_body)
      except Exception as e:
        self.logger.debug("SBServer Error: {}".format(e))
        return False
      except Exception:
        self.logger.debug("SqueezeBox Timeout")
        return False

  def stop(self):
    """ stop if playing """
    if self.running:
      resp = self.js_request_player(['stop'])
      self.logger.debug("Player stop: {}".format(resp))

  def destroy(self):
    self.t_stop.set()
    self.logger.debug("SqueezeBoxHandler stopped")


if __name__ == "__main__":
  import sys

  if len(sys.argv) < 3:
    print( '\n\t%s squeezeboxserver playername\n' % sys.argv[0])
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
