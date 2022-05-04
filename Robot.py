#! /usr/bin/python3
from settings import *
import pygame as pg
from comm.HubClient import ConnectionState
from time import sleep
from math import sqrt

def calculate_new_xy(old_xy, speed, angle_in_degrees):
    move_vec = pg.math.Vector2()
    move_vec.from_polar((speed, angle_in_degrees))
    return old_xy + move_vec

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
		
		self.pos = pg.math.Vector2(0,0)

		self.camera = self.app.camera

		self.speed = ROBOT_SPEED
		
		self.rotation = 0
		## For smoothing the rotation on the screen
		self.last_rotations = []
		self.max_last_rotations = ROTATION_SMOOTHING

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

		self.middle = None
		self.turning = False

		self.setup_robot()

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

		self.motor_stop(MOTOR_PORT)

		self.calibrate_steer(STEERING_CALIBRATING_SLOT, 3)

	def update_ports(self):
		for i in range(0, len(self.ports)):
			self.ports[i]["name"] = self.monitor.status.port_device_name(i)
			self.ports[i]["data"] = self.monitor.status.port_device_data(i)
		
	def clamp(self, num, min_value, max_value):
		return max(min(num, max_value), min_value)

	'''
	Starts running a motor at the given speed.

    If a keyword argument is not given, its default value will be used.

    Parameters

        speed : Sets the speed as a percentage of the rated speed for this motor. Positive means clockwise, negative means counterclockwise.
    Keyword Arguments

            max_power : Sets percentage of maximum power used during this command.

            acceleration : The time in milliseconds (0-10000) for the motor to reach maximum rated speed from standstill.

            deceleration : The time in milliseconds (0-10000) for the motor to stop when starting from the maximum rated speed.

            stall : Selects whether the motor should stop when stalled (True) or not (False).


	from: https://lego.github.io/MINDSTORMS-Robot-Inventor-hub-API/class_motor.html
	'''
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
		self.middle = self.get_motor_angle(STEERING_PORT_NUMERIC)

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


	def move(self):
		for port in self.ports:
			if port["name"] == "Distance Sensor":
				data = port["data"][0]
				length = None
				if data == None:
					length = 100
				else:
					length = data
				min_distance = 10
				initial_speed = -30
				sensitivity = 100
				speed = -((sqrt(abs(length*sensitivity)+min_distance)) + initial_speed)
				if speed > -4 and not self.turning:
					self.motor_stop(MOTOR_PORT)
					self.turning = True
					self.turn_automatic()
					self.turning = False
				else: 
					self.motor_start(MOTOR_PORT, speed, MOTOR_MAX_POWER, MOTOR_ACCELERATION, MOTOR_DECELERATION, True)
					'''
						First create a vector with only the length
						then rotate that vector to the correct angle
						then scale that point
					'''
				self.pos = calculate_new_xy(self.pos, -round(speed, 1)*0.03, -self.rotation+ROBOT_ROTATION_OFFSET)

		if self.get_motor_stall(MOTOR_NUMERIC_PORT) == MOTOR_STALL_VALUE:
			self.turn_automatic()

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
		if self.client.state == ConnectionState.TELEMETRY:
			self.rotate()
			self.move()
			self.update_ports()
			self.scan_points()
			self.update_rotation()
			print (self.pos)
	
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
			print (self.scanned_points[0])
			self.scanned_points[0]["object"].remove()
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