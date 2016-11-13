#!/usr/bin/python

import json
import socket
import urllib2


server = 'rpi'
server_port = 9000
player_name = 'Kitchen'
amp_port = 54321



url = 'http://' . server . ':' . server_port . '/jsonrpc.js'
def js_request(player_id,params):
    json_string = {
            "id": 1,
            "method": "slim.request",
            "params": [player_id, params],
    }

    header = {
        'Content-Type': 'application/json',
        'User-Agent': 'tpi',
        'Accept': 'application/json',
    }

    # craft the request for a url
    req = urllib2.Request(url, json.dumps(json_string), headers=header)

    # send the request
    res = urllib2.urlopen(req)
    return  json.loads(res.read())

def js_request2(params):
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
    req = urllib2.Request(url, json.dumps(json_string), headers=header)

    # send the request
    res = urllib2.urlopen(req)
    return  json.loads(res.read())


def is_playing(playerid):
        mode = js_request(playerid,["mode","?"])['result']['_mode']
        if mode == 'stop':
            return False
        return True

def get_player(name):
    playerid = None
    response =  js_request2(["",["serverstatus",0,999]])
    for player in response['result']['players_loop']:
        if player['name'] == name:
            playerid = player['playerid']

    return playerid

def serverstatus():
        """ {"id":1,"method":"slim.request","params":["",["serverstatus",0,999]]} """
        response =  js_request2(["",["serverstatus",0,999]])
        for player in response['result']['players_loop']:
            print "player", player['name'], player['playerid']

if __name__ == "__main__":
    serverstatus()
    playerid = get_player(player_name)
    if not is_playing(playerid):
        print "Shutting down Amp"
        amp_host = 'spi'
        urllib2.urlopen("http://%s:%i/AmpOFF" % (amp_host,amp_port)).read()


