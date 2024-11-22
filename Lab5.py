# Library imports
from vex import *


#Defining the states
IDLE = 0
LINE_FOLLOWING = 1
SEARCHING = 2
APPROACHING = 3

current_state = IDLE

# Create a new object "brain_inertial" with the
# Inertial class.
brain_inertial = Inertial(Ports.PORT15)


#Motor and sensor initialization:
brain=Brain()
left_motor=Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
right_motor=Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
arm_motor = Motor(Ports.PORT8, GearSetting.RATIO_18_1, False)
controller = Controller()
brain_inertial = Inertial(Ports.PORT16)

LineFollowerR = Line(brain.three_wire_port.g)
LineFollowerL = Line(brain.three_wire_port.h)

sonars = Sonar(brain.three_wire_port.c)
sonarb = Sonar(brain.three_wire_port.e)

timer = 0
# # Start calibration.
brain_inertial.calibrate()
wait(3, SECONDS)




# Create a new object "controller" with the Controller class.
controller = Controller()

# Define a function button_pressed().
def button_pressed():
    # The Brain will print that the button was pressed on the
    # Brain's screen.
    brain.screen.print("button pressed")


# # Start calibration.
# brain_inertial.calibrate()
# wait(3, SECONDS)

Vision16__LIMEFRUIT = Signature (1, -6835, -6333, -6584, -3507, -2897, -3202, 2.9, 0)
Vision16__LEMONFRUIT = Signature (2, 1357, 1797, 1577, -3425, -3035, -3230, 3, 0)
Vision16__ORANGEFRUIT = Signature (3, 5021, 6599, 5810, -2193, -1827, -2010, 3, 0)
Vision16__GRAPEFRUIT = Signature (4, 4645, 7421, 6033, -2811, -2019, -2415, 3, 0)

Vision3 = Vision (Ports.PORT9, 50, Vision16__LIMEFRUIT)



#Button Press to initialize the robot
def handleButton():
    global current_state

    if(current_state == IDLE):
        print('IDLE -> LINE_FOLLOWING') ## Pro-tip: print out state _transitions_
        current_state = LINE_FOLLOWING
        lineFollowing()

    else: ## failsafe; go to IDLE from any other state when button is pressed
        print(' -> IDLE')
        current_state = IDLE
        left_motor.stop()
        right_motor.stop()

controller.buttonA.pressed(handleButton)




# current snapshot = camera.take picture
# previous snapshot = false

# if current snapshot true and previous snapshot false
#     then do it
#     previous snapshot = current snapshot



# Line following 
def lineFollowing():
    brain_inertial.reset_heading()

    global current_state
    global timer
    global missedDetections



    while current_state == LINE_FOLLOWING:
        print("LINEFOLLOWING")
        print(timer)
    
        if LineFollowerL.reflectivity() > LineFollowerR.reflectivity():
            Delta = LineFollowerL.reflectivity() - LineFollowerR.reflectivity()
            LSpeed =  50 
            RSpeed =  50 + Delta
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
        if LineFollowerL.reflectivity() < LineFollowerR.reflectivity():
            Delta = LineFollowerR.reflectivity() - LineFollowerL.reflectivity()
            LSpeed =  50 + Delta
            RSpeed =  50
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
        if LineFollowerL.reflectivity() == LineFollowerR.reflectivity():
            LSpeed =  50
            RSpeed =  50 
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
            wait(1, MSEC)
        if sonars.distance(MM) < 450 and sonars.distance(MM) > 100 and sonars.distance(MM) > timer:
            current_state = SEARCHING
            print('LINEFOLLOWING -> SEARCHING')
            missedDetections = 0
            turn()
        if sonarb.distance(MM) < 100:
            turnRow()
        timer -= 1
        wait(5, MSEC)



def turnRow():
    while brain_inertial.heading() < 80:
        left_motor.spin(FORWARD, 30)
        right_motor.spin(FORWARD, -30)
    lineFollowing()

            





def turn():

    if current_state == SEARCHING:
        left_motor.spin(FORWARD, 30)
        right_motor.spin(FORWARD, -30)

        ## start the timer for the camera
        cameraTimer.event(cameraTimerCallback, 50)




# Searching for fruit NEW CODE
target_x = 160
K_x = 0.5
missedDetections = 0


cameraInterval = 50
cameraTimer = Timer()



# missedDetections = 0
# def handleLostObject():
#     global current_state
#     if current_state == APPROACHING:
#         print('APPROACHING -> SEARCHING') ## Pro-tip: print out state _transitions_
#         current_state = SEARCHING
#         left_motor.spin(FORWARD, 30)
#         right_motor.spin(FORWARD, -30)

def cameraTimerCallback():
    global current_state
    global missedDetections

    ## Here we use a checker-handler, where the checker checks if there is a new object detection.
    ## We don't use a "CheckForObjects()" function because take_snapshot() acts as the checker.
    ## It returns a non-empty list if there is a detection.
    objects = Vision3.take_snapshot(Vision16__LIMEFRUIT)
    # print(objects)
    if objects: handleObjectDetection()
    else: missedDetections = missedDetections + 1

    # restart the timer
    if(current_state == SEARCHING or current_state == APPROACHING):
        cameraTimer.event(cameraTimerCallback, 50)


def handleObjectDetection():
    global current_state
    global object_timer
    global missedDetections
# Need to make sure it goes for the object on the tree we want
    cx = Vision3.largest_object().centerX
    cy = Vision3.largest_object().centerY
    w = Vision3.largest_object().width
    h = Vision3.largest_object().height
    # print(cx)
    # print(cy)
    
  


    if current_state == SEARCHING and w > 20 and h > 20:
        print('SEARCHING -> APPROACHING') ## Pro-tip: print out state _transitions_
        current_state = APPROACHING

    ## Not elif, because we want the logic to cascade
    if current_state == APPROACHING:
        error = cx - target_x
        turn_effort = K_x * error

        right_motor.spin(FORWARD, 30 - turn_effort)
        left_motor.spin(FORWARD, 30 + turn_effort)

        if w > 166:
            touchedFruit()



    ## reset the time out timer
    missedDetections = 0

def checkForLostObject():
    if(missedDetections > 100): 
        return True

    else: 
        return False
    



def backOnLine():
    global current_state
    global timer
    global missedDetections

    missedDetections = 0

    if current_state == SEARCHING:
        print('LOOKING FOR LINE') ## Pro-tip: print out state _transitions_
        while brain_inertial.heading() > 3:
            left_motor.spin(FORWARD, -30)
            right_motor.spin(FORWARD, 30)
        # if brain_inertial.heading() < 10 or brain_inertial.heading() > 350:
         # left_motor.spin(FORWARD, 30)
        # right_motor.spin(FORWARD, 30)
        print('SEARCHING -> LINE_FOLLOWING') ## Pro-tip: print out state _transitions_
        timer = 1800
        current_state = LINE_FOLLOWING
        lineFollowing()
        # else:
            # print('LOOKING FOR LINE') ## Pro-tip: print out state _transitions_
            # left_motor.spin(FORWARD, -30)
            # right_motor.spin(FORWARD, 30)

def touchedFruit():
    left_motor.stop()
    right_motor.stop()

## Our main loop
while True:
    brain.screen.print_at("missed detections =", missedDetections, x=10, y=50)
    # brain.screen.print_at("variable =", timer, x=10, y=80)
    # brain.screen.print_at("reading =", sonars.distance(MM), x=10, y=120)
    ## if enough cycles have passed without a detection, we've lost the object
    if(checkForLostObject()): backOnLine()





