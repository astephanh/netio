#!/usr/bin/env python3

import logging,sys, os, time
import squeezebox

Server = 'hp'
Playername = 'Office'


if __name__=='__main__':
  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  logger = logging.getLogger(__name__)

  logger.info("starting")
  pl = squeezebox.Player(Server, Playername)

  try:
   while True:
     time.sleep(2)

  finally:
   pl.destroy()
   exit(0)
