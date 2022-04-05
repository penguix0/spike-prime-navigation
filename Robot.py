#! /usr/bin/python3

import yaml
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

# class Line(pg.sprite.Sprite):
# 	def __init__(self, app, origin=tuple, endpoint=tuple, color=tuple, thickness=float):
# 		# Call the parent class (Sprite) constructor
# 		self.groups = app.all_sprites
# 		pg.sprite.Sprite.__init__(self, self.groups)
# 		self.app = app
# 		self.origin = origin
# 		self.endpoint = endpoint
# 		self.color = color
# 		self.thickness = thickness
	
# 	def update(self):
# 		pg.draw.line(self.app.screen, self.color, self.origin, self.endpoint, self.thickness)

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
		self.x = DISPLAY_SIZE[0] / 2 - width / 2
		self.y = DISPLAY_SIZE[1] / 2 - height / 2

		self.rect.x = self.x
		self.rect.y = self.y

		self.speed = ROBOT_SPEED
		self.rotation = 0
		self.last_rotations = []
		self.max_last_rotations = 4

		self.setup_logger()

		self.status = None
				
		self.port_a = {"name": None, "data": None}
		self.port_b = {"name": None, "data": None}
		self.port_c = {"name": None, "data": None}
		self.port_d = {"name": None, "data": None}
		self.port_e = {"name": None, "data": None}
		self.port_f = {"name": None, "data": None}
		
		self.ports = [self.port_a, self.port_b, self.port_c, self.port_d, self.port_e, self.port_f]

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
		# self.x = -self.get_accelerometer()[0] * 0.1
		# self.x = self.clamp(self.x, 0, DISPLAY_SIZE[0] - self.width - 10)
		# self.rect.x = self.x
		
		# self.y += self.get_accelerometer()[1] * 0.1
		# ## - 10 for some spacing with the wall
		# self.y = self.clamp(self.y, 0, DISPLAY_SIZE[1] - self.height - 10)
		# self.rect.y = self.y
		pass

	"""rotate an image while keeping its center"""
	def rotate(self):
		self.rotation = (-self.get_orientation()[0])
		self.last_rotations.append(self.rotation)
		## If the list is becoming too long delete the oldest value
		if len(self.last_rotations) > self.max_last_rotations:
			self.last_rotations.pop(0)
		list_average = sum(self.last_rotations)/len(self.last_rotations)

		self.image = pg.transform.rotate(self.original_image, list_average)
		self.rect = self.image.get_rect(center = self.rect.center)

	def update(self):
		self.move()
		self.rotate()
		self.update_ports()
		self.draw_distance()

		for port in self.ports:
			if port["name"] == "Distance Sensor":
				print (port)
	
	def draw_distance(self):
		for port in self.ports:
			if port["name"] == "Distance Sensor":
				data = port["data"][0]
				if data != None:
					length = port["data"][0] * 100
					origin = (0, 0)
					endpoint = (length, length)
					pg.draw.line(self.app.screen, RED, origin, endpoint, 20)


	def get_accelerometer(self):
		data = self.monitor.status.accelerometer() 
		for i in range(len(data)):
			if not data[i] == '':	
				data[i] = float(data[i])
			else:
				data[i] = 0
		return data

	def processed_accelerometer(self):
		data = self.get_accelerometer()
		data[0] = data[0] - (abs(self.get_orientation()[2]) * (1000/90))
		data[1] = data[1]
		data[2] = data[2]
		
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