# Library imports
from vex import *


#Defining the states
# IDLE = 0
# LINE_FOLLOWING = 1
# SEARCHING = 2
# APPROACHING = 3

# current_state = IDLE



#Motor and sensor initialization:
brain=Brain()
left_motor=Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
right_motor=Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
arm_motor = Motor(Ports.PORT15, GearSetting.RATIO_18_1, False)
controller = Controller()
# brain_inertial = Inertial(Ports.PORT16)


LIMEFRUIT = Signature (1, -6291, -5615, -5953, -3457, -2907, -3182, 3, 0)
LEMONFRUIT = Signature (2, 1785, 4213, 2999, -4201, -3863, -4032, 3, 0)
ORANGEFRUIT = Signature (3, 5231, 8313, 6772, -3049, -2703, -2876, 3, 0)
GRAPEFRUIT = Signature (4, 6351, 8771, 7561, 493, 757, 625, 3, 0)

camera = Vision (Ports.PORT9, 50, LIMEFRUIT)



# Searching for fruit NEW CODE
target_y = 140
K_y = 0.5
missedDetections = 0


cameraInterval = 50
cameraTimer = Timer()

def cameraTimerCallback():
    objects = camera.take_snapshot(LIMEFRUIT)
    if objects: handleObjectDetection()

def handleObjectDetection():
    cx = camera.largest_object().centerX
    cy = camera.largest_object().centerY
    w = camera.largest_object().width
    h = camera.largest_object().height
    error = target_y - cy
    arm_effort = K_y * error

    arm_motor.spin(FORWARD, arm_effort)

    # if cy > target_y:
    #     arm_motor.spin(REVERSE, arm_effort)
    # if cy < target_y:
    #     arm_motor.spin(REVERSE, arm_effort)
    # print(cx)
    brain.screen.print(cy)
    print(arm_effort)

# def checkForLostObject():
#     if(missedDetections > 50): 
#         return True

#     else: 
#         return False





while True:
    cameraTimerCallback()
    # if (checkForLostObject()): arm_motor.stop()
    # else:
    #     cameraTimerCallback()
        





