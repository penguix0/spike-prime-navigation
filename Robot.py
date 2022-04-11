#! /usr/bin/python3

from tokenize import String
import yaml

from comm.HubClient import ConnectionState
with open("path.yaml") as file:
	try: 
		global pathConfig
		pathConfig = yaml.safe_load(file)
	except yaml.YAMLError as exc:
		print (exc)

from os import chdir
chdir(pathConfig["path"])

import os, sys

from settings import *
import pygame as pg

class Robot(pg.sprite.Sprite):
	def __init__(self, app, color, width, height):
		# Call the parent class (Sprite) constructor
		self.groups = app.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.app = app
		self.width = width
		self.height = height
		## pg.SRCALPHA makes the background of the sprite transparent, witho
		self.original_image = pg.Surface((self.width, self.height), pg.SRCALPHA)
		self.original_image.fill(color)
		self.image = self.original_image
		self.rect = self.original_image.get_rect()
		
		self.x = 0
		self.y = 0

		self.camera = self.app.camera

		self.speed = ROBOT_SPEED
		
		self.rotation = 0
		## For smoothing the rotation on the screen
		self.last_rotations = []
		self.max_last_rotations = ROTATION_SMOOTHING

		self.setup_logger()

		self.status = None
				
		self.port_a = {"name": None, "data": None}
		self.port_b = {"name": None, "data": None}
		self.port_c = {"name": None, "data": None}
		self.port_d = {"name": None, "data": None}
		self.port_e = {"name": None, "data": None}
		self.port_f = {"name": None, "data": None}
		
		self.ports = [self.port_a, self.port_b, self.port_c, self.port_d, self.port_e, self.port_f]

		## Points scanned by the ultra sonic sensor
		self.dummy_scan = {"robot_position": (0,0), "angle": 0, "length": 0}
		self.scanned_points = [self.dummy_scan]
		self.max_scanned_points = MAX_SCANNED_POINTS
		self.setup_robot()

	def setup_logger(self):
		from logging import getLogger
		from utils.setup import setup_logging
		self.logger = getLogger("App")

		log_filename = os.path.dirname(pathConfig["path"]) + "/logs/hubstatus.log"
		setup_logging(log_filename)

		self.logger.info("LEGO status app starting up")

	def setup_robot(self):
		from comm.HubClient import HubClient
		from data.HubMonitor import HubMonitor

		self.client = HubClient()

		self.client.start()

		self.monitor = HubMonitor(self.client)

	def update_ports(self):
		for i in range(0, len(self.ports)):
			self.ports[i]["name"] = self.monitor.status.port_device_name(i)
			self.ports[i]["data"] = self.monitor.status.port_device_data(i)
		
	def clamp(self, num, min_value, max_value):
		return max(min(num, max_value), min_value)

	def move(self):
		self.rect.centerx = self.x + self.camera.get_position()[0]
		self.rect.centery = self.y + self.camera.get_position()[1]
	
	def scale(self):
		pass

	"""rotate an image while keeping its center and smooth the rotation"""
	def rotate(self):
		self.rotation = (-self.get_orientation()[0])
		self.last_rotations.append(self.rotation)
		## If the list is becoming too long delete the oldest value
		if len(self.last_rotations) > self.max_last_rotations:
			self.last_rotations.pop(0)
		list_average = sum(self.last_rotations) / len(self.last_rotations)

		self.image = pg.transform.rotozoom(self.original_image, list_average, 1)
		self.rect = self.image.get_rect(center = self.rect.center)

	def update(self):
		self.scale()
		self.rotate()
		self.move()
		## Prevent the program from requesting things from the hub while it's not connected.
		if self.client.state == ConnectionState.TELEMETRY:
			self.update_ports()
			self.scan_points()
	
	
	def scan_points(self):
		for port in self.ports:
			if port["name"] == "Distance Sensor":
				data = port["data"][0]
				if data == None:
					break
				length = port["data"][0]
				self.scanned_points.append({"robot_position": (self.rect.centerx, self.rect.centery), "angle": self.rotation, "length": length})
		## Prevent the scanned points from getting to big and causing lag
		if len(self.scanned_points) > self.max_scanned_points:
			self.scanned_points.pop(0)

	def get_accelerometer(self):
		data = self.monitor.status.accelerometer() 
		for i in range(len(data)):
			if not data[i] == '':	
				data[i] = float(data[i])
			else:
				data[i] = 0
		return data

	def get_gyroscope(self):
		data = self.monitor.status.gyroscope() 
		for i in range(len(data)):
			if not data[i] == '':	
				data[i] = float(data[i])
			else:
				data[i] = 0
		return data

	def get_orientation(self):
		data = self.monitor.status.orientation()
		for i in range(len(data)):
			if data[i] == '':	
				data[i] = 0
		return data