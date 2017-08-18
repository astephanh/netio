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
    self.player = player
    self.playerid = None
    self.running = False

    self.t_stop = Event()
    self.lock = Lock()
    self.t = Thread(target=self.watch_player, args=(1, self.t_stop))
    self.t.start()
    self.logger.info("PlayerThread started, %s" % self.player)

  def watch_player(self, arg1, stop_event):
    while(not stop_event.is_set()):
      self._check_if_running()
      time.sleep(3)

  def _check_if_running(self):
    """ check if tv is running """
    if not self.playerid:
      self.playerid = self.get_player(self.player)
      self.logger.info("Player %s has ID: %s" % (self.player,self.playerid))

    if self.playerid:
      mode = self.js_request(["mode","?"])['result']['_mode']
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

  def js_request(self,params):
      json_string = {
              "id": 1,
              "method": "slim.request",
              "params": [self.playerid, params],
      }

      header = {
          'Content-Type': 'application/json',
          'User-Agent': 'tpi',
          'Accept': 'application/json',
      }

      # craft the request for a url
      req = urllib2.Request(self.url, json.dumps(json_string), headers=header)

      # send the request
      res = urllib2.urlopen(req)
      return  json.loads(res.read())

  def js_request2(self,params):
      json_string = {
              "id": 1,
              "method": "slim.request",
              "params": params,
      }

      header = {
          'Content-Type': 'application/json',
          'User-Agent': 'tpi',
          'Accept': 'application/json',
      }

      # craft the request for a url
      req = urllib2.Request(self.url, json.dumps(json_string), headers=header)

      # send the request
      res = urllib2.urlopen(req)
      return  json.loads(res.read())

  def is_playing(self):
    mode = self.js_request(["mode","?"])['result']['_mode']
    if mode == 'stop' or mode == "pause":
      return False
    return True

  def stop(self):
    """ stop if playing """
    resp = self.js_request(['stop'])
    self.logger.debug("Player stop: %s" % resp)

  def get_player(self,name):
    playerid = None
    response =  self.js_request2(["",["serverstatus",0,999]])
    for player in response['result']['players_loop']:
      if player['name'] == name:
        playerid = player['playerid']
    return playerid

  def serverstatus(self):
    """ {"id":1,"method":"slim.request","params":["",["serverstatus",0,999]]} """
    response =  self.js_request2(["",["serverstatus",0,999]])
    for player in response['result']['players_loop']:
      print "player", player['name'], player['playerid']

  def destroy(self):
    self.t_stop.set()
    self.logger.debug("PlayerThread stopped")


if __name__ == "__main__":
  import sys

  if len(sys.argv) < 3:
    print '\n\t%s squeezeboxserver playername\n' % sys.argv[0]
    exit(0)

    #serverstatus()
    playerid = get_player(player_name)
    if not is_playing():
        urllib2.urlopen("http://%s:%i/AmpOFF" % (amp_host,amp_port)).read()

