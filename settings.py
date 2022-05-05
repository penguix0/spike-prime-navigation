DISPLAY_SIZE = (1280, 720)
TITLE = "Test"
FPS = 60

TEXT_SIZE = 24


## Ziek
WALKING_CHANCE = 2
STANDING_CHANCE = 4
RESTING_CHANCE = 3
EATING_CHANCE = 1
ACTIVITY_TIME_SICK = 1000

## NORMAAL
WALKING_CHANCE = 30
STANDING_CHANCE = 20
RESTING_CHANCE = 30
EATING_CHANCE = 20
ACTIVITY_TIME_NORMAL = 1000

## How higher this number, how more often the nek will go down.
NEK_ACTIVATE_CHANCE_NORMAL = 1000
## How higher this number, how longer the nek will go down.
NEK_DURATION_CHANCE_NORMAL = 500

## Colors ##

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
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
MOTOR_NUMERIC_PORT = 1
MOTOR_SPEED = -100
MIN_MOTOR_SPEED = -10
MOTOR_BACKING_SPEED = 100
MOTOR_MAX_POWER = 100
MOTOR_ACCELERATION = 1
MOTOR_DECELERATION = 1
MOTOR_STALL_VALUE = -100

STEERING_PORT = "A"
STEERING_PORT_NUMERIC = 0
STEERING_SPEED = 100
STEERING_MAX_POWER = 50
STEERING_ACCELERATION = 10
STEERING_DECELERATION = 10
## Angle difference between middle and left or right.
STEERING_TURNING_ANGLE = 70
STEERING_LEFT = 60
STEERING_MIDDLE = 0
STEERING_RIGHT = -60
## this slot on the hub holds a small program whichs centers the steering wheel, this program is made by lego itself and can be found in the home edition of lego mindstorms robot inventor:
## When program is started
## M.V.P. calibrate
STEERING_CALIBRATING_SLOT = 15

DISTANCE_TO_STOP = 10

TRACKER_PORT = "D"
TRACKER_PORT_NUMERIC = 3
TRACKER_SPEED = 20
TRACKER_MAX_POWER = 0.05
TRACKER_STALL = 40
TRACKER_DOWN_ANGLE = 0
TRACKER_UP_ANGLE = -90

## Dots
DOT_SIZE = 5

## Camera
INITIAL_CAMERA_POS_X = DISPLAY_SIZE[0] / 2
INITIAL_CAMERA_POS_Y = DISPLAY_SIZE[1] / 2
INITIAL_ZOOM = 2
