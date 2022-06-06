#! /usr/bin/python3
from xmlrpc.client import FastParser
from settings import *
import pygame as pg
from comm.HubClient import ConnectionState
from time import sleep
from math import sqrt
import threading
import random

def calculate_new_xy(old_xy, speed, angle_in_degrees):
    move_vec = pg.math.Vector2()
    move_vec.from_polar((speed, angle_in_degrees))
    return old_xy + move_vec

class Robot(pg.sprite.Sprite):
	def __init__(self, app, color, width, height):
		## ---===== Setup =====----
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
		
		self.pos = pg.math.Vector2(0,0)

		self.camera = self.app.camera

		self.speed = 0
		self.real_world_speed = 0
		self.distance_droven = 0
		
		## ---===== Rotation =====----
		self.rotation = 0
		## For smoothing the rotation on the screen
		self.last_rotations = []
		self.max_last_rotations = ROTATION_SMOOTHING

		self.status = None

		## ---===== Ports =====----			
		self.port_a = {"name": None, "data": None}
		self.port_b = {"name": None, "data": None}
		self.port_c = {"name": None, "data": None}
		self.port_d = {"name": None, "data": None}
		self.port_e = {"name": None, "data": None}
		self.port_f = {"name": None, "data": None}
		
		self.ports = [self.port_a, self.port_b, self.port_c, self.port_d, self.port_e, self.port_f]

		self.sensor_distance = 0
		self.servo_sensor_angle = 0


		## ---===== Scanning =====----
		## Points scanned by the ultra sonic sensor
		self.dummy_scan = {"robot_position": (-100,-100), "angle": 0, "length": 0}
		self.scanned_points = [self.dummy_scan]
		self.max_scanned_points = MAX_SCANNED_POINTS

		## ---===== Steering =====----
		self.middle = None
		self.turning = False

		## ---===== Tracking =====----
		self.tracker_down = False
		self.tracker_up = False
		self.tracker_state = "Gebruik de nummers 9 & 0 om de 'nek' te bedienen in auto modus"

		self.setup_complete = False
		setup_function = threading.Thread(target=self.setup_robot)
		setup_function.start()

	def setup_robot(self):
		from comm.HubClient import HubClient
		from data.HubMonitor import HubMonitor

		self.client = HubClient()

		self.client.start()

		self.monitor = HubMonitor(self.client)

		while not self.client.state == ConnectionState.TELEMETRY:
			sleep(0.5)
			print (".", end="")
		
		self.motor_stop(MOTOR_PORT)

		self.calibrate_steer(1)
		
		#self.calibrate_tracker(TRACKER_PORT)

		self.setup_complete = True

	## Motors

	def update_ports(self):
		for i in range(0, len(self.ports)):
			self.ports[i]["name"] = self.monitor.status.port_device_name(i)
			self.ports[i]["data"] = self.monitor.status.port_device_data(i)

	def motor_start(self, port, speed, max_power, acceleration, deceleration, stall):
		self.client.send_message('scratch.motor_start', {'port': port, 'speed': speed, 'max_power': max_power, 'acceleration': acceleration, 'deceleration': deceleration, 'stall': stall})
	
	def motor_stop(self, port):
		self.client.send_message('scratch.motor_stop', {'port': port, 'stop':0})
	
	def get_motor_angle(self, port):
		return self.monitor._status.port_raw(port)[1][2]
	
	def get_motor_stall(self, port):
		return self.monitor._status.port_raw(port)[1][3]

	def get_motor_speed(self, port):
		return self.monitor._status.port_raw(port)[1][0]
	
	def set_motor_angle(self, port, speed, position, stall):
		self.client.send_message('scratch.motor_go_to_relative_position', { 'port': port, 'speed': speed, 'position': position, 'stall': stall, 'stop': True})
		
	def set_motor_absolute_angle(self, port, speed, direction, position, stall):
		self.client.send_message_without_response('scratch.motor_go_direction_to_position', { 'port': port, 'speed': speed, 'position': position,  'direction': direction, 'stall': stall, 'stop': True})
	
	def motor_run_for_degrees(self, port, speed, stall, stop, degrees):
		self.client.send_message_without_response('scratch.motor_run_for_degrees', { 'port': port, 'speed': speed, 'stall': stall, 'stop': stop,'degrees': degrees})

	## Calibrating

	def calibrate_steer(self, time):
		self.motor_start(STEERING_PORT, STEERING_SPEED, STEERING_MAX_POWER, STEERING_ACCELERATION, STEERING_ACCELERATION, 80)
		sleep(time)
		self.set_motor_angle(STEERING_PORT, STEERING_SPEED, STEERING_MIDDLE, 80)

		
	## Turning

	def turn_left(self, port, speed):
		self.set_motor_angle(port, speed, STEERING_LEFT, True)

	def turn_right(self, port, speed):
		self.set_motor_angle(port, speed, STEERING_RIGHT, True)

	def turn_center(self, port, speed):
		self.set_motor_angle(port, speed, STEERING_MIDDLE, True)

	## Moving

	def move_tracker_up(self):
		if not self.tracker_up:
			self.set_motor_absolute_angle(TRACKER_PORT, TRACKER_SPEED, 'counterclockwise', TRACKER_UP_ANGLE, TRACKER_STALL)
			self.tracker_up = True
			self.tracker_down = False

	def move_tracker_down(self):
		if not self.tracker_down:
			self.set_motor_absolute_angle(TRACKER_PORT, TRACKER_SPEED, 'clockwise', TRACKER_DOWN_ANGLE, TRACKER_STALL)
			self.tracker_up = False
			self.tracker_down = True

	def move(self):
		self.speed = self.get_motor_speed(MOTOR_NUMERIC_PORT)
		for port in self.ports:
			if port["name"] == "Distance Sensor":
				data = port["data"][0]
				if data == None:
					self.sensor_distance = 100
				else:
					self.sensor_distance = data

		self.servo_sensor_angle = self.get_motor_angle(SENSOR_SERVO_PORT_NUMERIC)
		self.real_world_speed = -1 * float(self.speed / 100) * float(REAL_WORLD_SPEED_AT_100_PRECENT)
		self.distance_droven += self.real_world_speed * self.app.deltaTime
		## Calculate the new position based on the speed
		self.pos = calculate_new_xy(self.pos, round(self.speed, 1)*0.03, -self.rotation+ROBOT_ROTATION_OFFSET)
		
		## Rotate/move the robot on the screen
		self.rect.centerx = self.pos.x + self.camera.get_position()[0]
		self.rect.centery = self.pos.y + self.camera.get_position()[1]

	def update_rotation(self):
		self.rotation = (self.get_orientation()[0])

	"""rotate an image while keeping its center and smooth the rotation"""
	def rotate(self):
		self.update_rotation()

		## Smooth rotation
		self.last_rotations.append(self.rotation)
		## If the list is becoming too long delete the oldest value
		if len(self.last_rotations) > self.max_last_rotations:
			self.last_rotations.pop(0)
		list_average = sum(self.last_rotations) / len(self.last_rotations)

		## Apply rotation
		self.image = pg.transform.rotozoom(self.original_image, list_average, 1)
		self.rect = self.image.get_rect(center = self.rect.center)

	def update(self):
		## Prevent the program from requesting things from the hub while it's not connected.
		if self.setup_complete:
			if self.client.state == ConnectionState.TELEMETRY:
				self.rotate()
				self.move()
				self.update_ports()
				self.scan_points()
				self.update_rotation()
			else:
				self.app.quit()

	def scan_points(self):
		for port in self.ports:
			if port["name"] == "Distance Sensor":
				data = port["data"][0]
				if data == None:
					break
				length = data
				self.scanned_points.append({"robot_position": (self.rect.centerx, self.rect.centery), "angle": self.rotation + self.servo_sensor_angle, "length": length})
		## Prevent the scanned points from getting to big and causing lag
		if len(self.scanned_points) > self.max_scanned_points:
			self.scanned_points.pop(0)

	## Movement sensors

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