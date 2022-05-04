#! /usr/bin/python3
from settings import *
import pygame as pg
from comm.HubClient import ConnectionState
from time import sleep
from math import sqrt
import threading

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

		self.speed = ROBOT_SPEED
		
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


		## ---===== Scanning =====----
		## Points scanned by the ultra sonic sensor
		self.dummy_scan = {"robot_position": (-100,-100), "angle": 0, "length": 0}
		self.scanned_points = [self.dummy_scan]
		self.max_scanned_points = MAX_SCANNED_POINTS

		## ---===== Steering =====----
		self.middle = None
		self.turning = False

		## ---===== Tracking =====----
		self.tracker_down = None
		self.tracker_state = "Gebruik de nummers 9 & 0 om de 'nek' te bedienen"
		self.tracker_moved = True
		self.tracker_calibrated = False

		self.setup_complete = False
		setup_function = threading.Thread(target=self.setup_robot)
		setup_function.start()

	def setup_robot(self):
		from comm.HubClient import HubClient
		from data.HubMonitor import HubMonitor

		self.client = HubClient()

		self.client.start()

		self.monitor = HubMonitor(self.client)

		print ("Connecting")
		while not self.client.state == ConnectionState.TELEMETRY:
			sleep(0.5)
			print (".", end="")
		
		self.setup_complete = True

		self.motor_stop(MOTOR_PORT)

		self.calibrate_steer(STEERING_CALIBRATING_SLOT, 3)
		
		self.calibrate_tracker(TRACKER_PORT)
		
		turn_tracker = threading.Thread(target=self.turn_tracker)
		turn_tracker.start()

	def update_ports(self):
		for i in range(0, len(self.ports)):
			self.ports[i]["name"] = self.monitor.status.port_device_name(i)
			self.ports[i]["data"] = self.monitor.status.port_device_data(i)
		
	def clamp(self, num, min_value, max_value):
		return max(min(num, max_value), min_value)

	def motor_start(self, port, speed, max_power, acceleration, deceleration, stall):
		self.client.send_message('scratch.motor_start', {'port': port, 'speed': speed, 'max_power': max_power, 'acceleration': acceleration, 'deceleration': deceleration, 'stall': stall})
	
	def motor_stop(self, port):
		self.client.send_message('scratch.motor_stop', {'port': port, 'stop':0})
	
	def get_motor_angle(self, port):
		return self.monitor._status.port_raw(port)[1][2]
	
	def get_motor_stall(self, port):
		return self.monitor._status.port_raw(port)[1][3]
	
	def set_motor_angle(self, port, speed, position, stall):
		self.client.send_message('scratch.motor_go_to_relative_position', { 'port': port, 'speed': speed, 'position': position, 'stall': stall, 'stop': True})
	
	def motor_run_for_degrees(self, port, speed, stall, stop, degrees):
		self.client.send_message('scratch.motor_run_for_degrees', { 'port': port, 'speed': speed, 'stall': stall, 'stop': stop,'degrees': degrees})

	def calibrate_steer(self, port, time):
		self.client.program_execute(port)
		sleep(time)
		self.client.program_terminate()
		self.client.send_message('scratch.display_clear')
		self.middle = self.get_motor_angle(STEERING_PORT_NUMERIC)
	
	def calibrate_tracker(self, port):
		## Get the motor angle facing downwards
		self.motor_start(port, TRACKER_SPEED, TRACKER_MAX_POWER, 1, 1, 1)
		motor_stalled = False
		while not motor_stalled:
			sleep(0.01)
			if self.get_motor_stall(TRACKER_PORT_NUMERIC) >= TRACKER_STALL:
				motor_stalled = True
		self.motor_stop(TRACKER_PORT)

		self.tracker_down = self.get_motor_angle(TRACKER_PORT_NUMERIC)

		## Move the motor up for a certain amaount of degrees
		self.motor_start(port, -TRACKER_SPEED, TRACKER_MAX_POWER, 1, 1, 1)
		correct_pos = False
		while not correct_pos:
			sleep(0.01)
			if self.get_motor_angle(TRACKER_PORT_NUMERIC) < self.tracker_down - TRACKER_FLAT_ANGLE:
				correct_pos = True
		self.motor_stop(TRACKER_PORT)

		self.tracker_calibrated = True
		
	def turn_left(self, port, speed):
		self.set_motor_angle(port, speed, STEERING_LEFT, True)

	def turn_right(self, port, speed):
		self.set_motor_angle(port, speed, STEERING_RIGHT, True)

	def turn_center(self, port, speed):
		self.set_motor_angle(port, speed, STEERING_MIDDLE, True)

	def turn_automatic(self):
		self.turn_left(STEERING_PORT, STEERING_SPEED)

		self.motor_start(MOTOR_PORT, MOTOR_BACKING_SPEED, MOTOR_MAX_POWER, MOTOR_ACCELERATION, MOTOR_DECELERATION, True)

		sleep(1)

		self.turn_right(STEERING_PORT, STEERING_SPEED)

		self.motor_start(MOTOR_PORT, MOTOR_SPEED, MOTOR_MAX_POWER, MOTOR_ACCELERATION, MOTOR_DECELERATION, True)

		sleep(1)

		self.turn_center(STEERING_PORT, STEERING_SPEED)

		self.motor_stop(MOTOR_PORT)

	def turn_tracker(self):
		while self.client.state == ConnectionState.TELEMETRY:
			if self.tracker_state == True and self.tracker_moved == False:
				## Move the tracker downwards
				self.motor_start(TRACKER_PORT, TRACKER_SPEED, TRACKER_MAX_POWER, 1, 1, 1)
				motor_stalled = False
				while not motor_stalled:
					if self.get_motor_stall(TRACKER_PORT_NUMERIC) >= TRACKER_STALL:
						sleep(0.05)
						motor_stalled = True
				self.motor_stop(TRACKER_PORT)
				self.tracker_moved = True
			elif self.tracker_state == False and self.tracker_moved == False:		
				## Move the motor up for a certain amaount of degrees
				self.motor_start(TRACKER_PORT, -TRACKER_SPEED, TRACKER_MAX_POWER, 1, 1, 1)
				correct_pos = False
				while not correct_pos:
					sleep(0.01)
					if self.get_motor_angle(TRACKER_PORT_NUMERIC) < self.tracker_down - TRACKER_FLAT_ANGLE:
						sleep(0.05)
						correct_pos = True
					if self.get_motor_stall(TRACKER_PORT_NUMERIC) >= TRACKER_STALL:
						correct_pos = True
				self.motor_stop(TRACKER_PORT)
				self.tracker_moved = True

	def move(self):
		if self.app.mode_text != "Auto" and self.setup_complete:
			length = 0
			for port in self.ports:
				if port["name"] == "Distance Sensor":
					data = port["data"][0]
					if data == None:
						length = 100
					else:
						length = data
			
			min_distance = 10
			initial_speed = -30
			sensitivity = 100
			self.speed = -((sqrt(abs(length*sensitivity)+min_distance)) + initial_speed)
			if self.speed > -4 and not self.turning:
				self.motor_stop(MOTOR_PORT)
				self.turning = True
				self.turning = False
			else: 
				self.motor_start(MOTOR_PORT, self.speed, MOTOR_MAX_POWER, MOTOR_ACCELERATION, MOTOR_DECELERATION, True)
				'''
					First create a vector with only the length
					then rotate that vector to the correct angle
					then scale that point
				'''
			self.pos = calculate_new_xy(self.pos, -round(self.speed, 1)*0.03, -self.rotation+ROBOT_ROTATION_OFFSET)

			if self.get_motor_stall(MOTOR_NUMERIC_PORT) == MOTOR_STALL_VALUE:
				self.turn_automatic()

		else:
			self.motor_start(MOTOR_PORT, self.speed, MOTOR_MAX_POWER, MOTOR_ACCELERATION, MOTOR_DECELERATION, True)

		self.pos = calculate_new_xy(self.pos, -round(self.speed, 1)*0.03, -self.rotation+ROBOT_ROTATION_OFFSET)
		## Rotate the robot on the screen
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
	
	def scan_points(self):
		for port in self.ports:
			if port["name"] == "Distance Sensor":
				data = port["data"][0]
				if data == None:
					break
				length = data
				self.scanned_points.append({"robot_position": (self.rect.centerx, self.rect.centery), "angle": self.rotation, "length": length})
		## Prevent the scanned points from getting to big and causing lag
		if len(self.scanned_points) > self.max_scanned_points:
			self.scanned_points.pop(0)

	def set_display_text(self, text):
		self.client.send_message('scratch.display_text', {'text':text})

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