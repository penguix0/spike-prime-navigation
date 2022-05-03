DISPLAY_SIZE = (1280, 720)
TITLE = "Test"
FPS = 29.97

## Colors ##

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BGCOLOR = BLACK

## Robot ##
ROBOT_WIDTH = 10
ROBOT_HEIGHT = 20
ROBOT_ROTATION_OFFSET = 90

ROBOT_SPEED = 1

ROTATION_SMOOTHING = 4
MAX_SCANNED_POINTS = 3

MOTOR_PORT = "B"
MOTOR_SPEED = -100
MOTOR_BACKING_SPEED = 100
MOTOR_MAX_POWER = 100
MOTOR_ACCELERATION = 1000
MOTOR_DECELERATION = 1

STEERING_PORT = "A"
STEERING_PORT_NUMERIC = 0
STEERING_SPEED = 100
STEERING_MAX_POWER = 50
STEERING_ACCELERATION = 10
STEERING_DECELERATION = 10
## Angle difference between middle and left or right.
STEERING_TURNING_ANGLE = 70
STEERING_LEFT = 70
STEERING_MIDDLE = 0
STEERING_RIGHT = -70
## this slot on the hub holds a small program whichs centers the steering wheel, this program is made by lego itself and can be found in the home edition of lego mindstorms robot inventor:
## When program is started
## M.V.P. calibrate
STEERING_CALIBRATING_SLOT = 15

## Dots
DOT_SIZE = 5

## Camera
INITIAL_CAMERA_POS_X = DISPLAY_SIZE[0] / 2
INITIAL_CAMERA_POS_Y = DISPLAY_SIZE[1] / 2
INITIAL_ZOOM = 2
