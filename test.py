#!/usr/bin/env python3

# Run a command on the hub.
# Guts were lifted from spikeprime-tools/spiketools/spikejsonrpcapispike.py

import base64
import os
import argparse
from tqdm import tqdm
import time
import logging
from datetime import datetime
from comm.HubClient import ConnectionState, HubClient
from data.HubMonitor import HubMonitor
from utils.setup import setup_logging
import mpy_cross
from pathlib import Path

logger = logging.getLogger("App")


class RPC:
  def __init__(self):
    self._client = HubClient()
    self._hm = HubMonitor(self._client)
    self._hm.events.console_print += self._console_print
    self._client.start()
    
  def _console_print(self, msg):
    print(msg, end='')
    
  def _gen_random_id(self, length=4):
    import string, random
    letters = string.ascii_letters + string.digits + '_'
    return ''.join(random.choice(letters) for _ in range(length))  

  def send_message(self, name, params = {}):
    while rpc._client.state is not ConnectionState.TELEMETRY:
      logger.info('waiting for hub to connect')
      time.sleep(0.2)
    return self._client.send_message(name, params)

  def move_project(self, from_slot, to_slot):
    return self.send_message('move_project', {'old_slotid': from_slot, 'new_slotid': to_slot})

  def remove_project(self, from_slot):
    return self.send_message('remove_project', {'slotid': from_slot })

# Light Methods
  def display_set_pixel(self, x, y, brightness = 9):
    return self.send_message('scratch.display_set_pixel', { 'x':x, 'y': y, 'brightness': brightness})

  def display_clear(self):
    return self.send_message('scratch.display_clear')

  def display_image(self, image):
    return self.send_message('scratch.display_image', { 'image':image })

  def display_image_for(self, image, duration_ms):
    return self.send_message('scratch.display_image_for', { 'image':image, 'duration': duration_ms })

  def display_text(self, text):
    return self.send_message('scratch.display_text', {'text':text})

# Hub Methods
  def get_firmware_info(self):
    return self.send_message('get_hub_info')


if __name__ == "__main__":
  rpc = RPC()
  log_level = logging.WARNING
  setup_logging(os.path.dirname(__file__) + "/logs/run_command.log", log_level)

  rpc.send_message('scratch.motor_start', {'port':'B', 'speed':100, 'stall':True})
  time.sleep(1)
  rpc.send_message('scratch.motor_stop', {'port':'B', 'stop':0})
