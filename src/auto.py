#AXOBOTL Python Code
# Extreme Axolotls Robotics team 4028X for 2023-2024 VEX IQ Full Volume Challenge
from vex import *
import time

# The Eye class is useful for us
# Represents a Distance sensor that broadcasts if it "sees" an object

class Eye:
    def __init__(self, portNumber: int, distanceThreshold: int, units: DistanceUnits.DistanceUnits = DistanceUnits.MM):
        self.sensor = Distance(portNumber)
        self.distanceThreshold: int = distanceThreshold
        self.units = units
        self.seen: bool = False  # Variables keep us from broadcast()-ing repeatedly
        self.lost: bool = False
        self.eventSeen = None
        self.eventLost = None

    def setCallbacks(self, callbackSeen, callbackLost):
        self.eventSeen = Event(callbackSeen)
        self.eventLost = Event(callbackLost)

    def isObjectVisible(self) -> bool:
        return True if self.sensor.object_distance(self.units) <= self.distanceThreshold else False
    
    def look(self) -> bool:
        if self.sensor.installed():
            if self.isObjectVisible():
                if not self.seen:
                    self.seen = True
                    self.lost = False
                    if self.eventSeen: self.eventSeen.broadcast()
                    return True
            else:
                if not self.lost:
                    self.seen = False
                    self.lost = True
                    if self.eventLost: self.eventLost.broadcast()
        return False

# Setup
brain = Brain()
inertial = Inertial()

wheelLeft = Motor(Ports.PORT7, 2.0, True)  # Gear ratio: 2:1
wheelRight = Motor(Ports.PORT12, 2.0, False)
intakeEye = Eye(Ports.PORT6, 80, MM)
topEye = Eye(Ports.PORT5, 35, MM)
catEye = Eye(Ports.PORT2, 80, MM)
catBeltLeft = Motor(Ports.PORT3)
catBeltRight = Motor(Ports.PORT11,True)
intakeLeft = Motor(Ports.PORT4, True)
intakeRight = Motor(Ports.PORT1)
ledLeft = Touchled(Ports.PORT10)
ledRight = Touchled(Ports.PORT9)
buttBumper = Bumper(Ports.PORT8)
ballHugger = Pneumatic(Ports.PORT10)
screenColor: Color.DefinedColor = Color.BLUE
penColor: Color.DefinedColor = Color.WHITE
catBeltRunning: bool = False
intakeRunning: bool = False
cancelGoStraight: bool = False
isContinuousCallback = None

wait(15, MSEC)  # Allow events and everything else to initialize

def setup():
    clearScreen()
    updateMotor(wheelLeft, 0.0, FORWARD)
    updateMotor(wheelRight, 0.0, FORWARD)
    wheelLeft.set_max_torque(100, PERCENT)
    wheelRight.set_max_torque(100, PERCENT)

    intakeLeft.set_velocity(100, PERCENT)
    intakeRight.set_velocity(100, PERCENT)
    intakeLeft.set_max_torque(100, PERCENT)
    intakeRight.set_max_torque(100, PERCENT)

    catBeltLeft.set_velocity(100, PERCENT)
    catBeltRight.set_velocity(100, PERCENT)
    catBeltLeft.set_max_torque(100, PERCENT)
    catBeltRight.set_max_torque(100, PERCENT)
    setupCatBelt()

def clearScreen(screenColor = None, penColor = None):
    screenColor = screenColor if screenColor is None else screenColor
    penColor = penColor if penColor is None else penColor
    brain.screen.clear_screen()
    brain.screen.set_fill_color(screenColor)
    brain.screen.set_pen_color(screenColor)
    brain.screen.draw_rectangle(0, 0, 170, 100, screenColor)
    brain.screen.set_pen_color(penColor)
    brain.screen.set_font(FontType.MONO20)
    brain.screen.set_cursor(1, 1)

def brainPrint(message):
    brain.screen.print(message)
    brain.screen.new_line()
    print(message)  # For connected console

def onButtBumperPressed():
    pass

def onButtBumperReleased():
    pass

def onIntakeBallSeen():
    if topEye.isObjectVisible(): stopIntake()

def onIntakeBallLost():
    pass

def onTopBallSeen():
    if not isContinuousCallback or not isContinuousCallback():
        if intakeEye.isObjectVisible(): stopIntake()
        releaseHug()

def onTopBallLost():
    if topEye.isObjectVisible():
        if not catEye.isObjectVisible():
            stopIntake()
            windCat()
        if not topEye.isObjectVisible() and intakeEye.isObjectVisible(): spinIntake(REVERSE)

def updateMotor(motor: Motor,
                velocityPercent: float,
                direction: DirectionType.DirectionType = FORWARD,
                brakeType: BrakeType.BrakeType = COAST,
                timeoutSecs: float = 0.0,
                spinNow: bool = True,
                resetPosition: bool = False):
    motor.set_velocity(velocityPercent, PERCENT)
    motor.set_stopping(brakeType)
    if timeoutSecs > 0.0: motor.set_timeout(timeoutSecs, SECONDS)
    if spinNow: motor.spin(direction)
    if resetPosition: motor.set_position(0, RotationUnits.REV)

def updateDriveTrain(velocityPercent: float,
                     direction: DirectionType.DirectionType = FORWARD,
                     brakeType: BrakeType.BrakeType = COAST,
                     timeoutSecs: float = 0.0,
                     spinNow: bool = True,
                     resetPosition: bool = False):
    updateMotor(wheelLeft, velocityPercent, direction, brakeType, timeoutSecs, spinNow, resetPosition)
    updateMotor(wheelRight, velocityPercent, direction, brakeType, timeoutSecs, spinNow, resetPosition)

def stopDriveTrain(brakeType: BrakeType.BrakeType = COAST):
    wheelLeft.stop(brakeType)
    wheelRight.stop(brakeType)

def setupCatBelt(velocity: int = 100):
    updateMotor(catBeltLeft, velocity, brakeType=HOLD, spinNow=False)
    updateMotor(catBeltRight, velocity, brakeType=HOLD, spinNow=False)
    buttBumper.pressed(onBumperPressed)
    #buttBumper.released(onBumperReleased)
    ballHugger.pump_on()

def spinIntake(direction: DirectionType.DirectionType):
    intakeLeft.spin(direction)
    intakeRight.spin(direction) # Motor is configured reverse
    intakeRunning = True

def stopIntake(mode = HOLD):
    intakeLeft.stop(mode)
    intakeRight.stop(mode)
    intakeRunning = False

def startIntake():
    if not catEye.isObjectVisible(): windCat()
    if isContinuousCallback and isContinuousCallback(): hugBall()
    else: releaseHug(stop=True)  # Open up for the next ball
    spinIntake(REVERSE)

def reverseIntake():
    spinIntake(FORWARD)

def startBelt():
    hugBall()
    catBeltLeft.spin(REVERSE)
    catBeltRight.spin(REVERSE)
    catBeltRunning = True

def stopCatAndBelt():
    catBeltLeft.stop(HOLD)
    catBeltRight.stop(HOLD)
    catBeltRunning = False

def onBumperPressed():
    brain.play_sound(SoundType.TADA)
    ledLeft.set_color(Color.GREEN)
    buttBumperPressed.broadcast()

def windCat():  # Up Button
    releaseHug()
    catBeltLeft.spin(FORWARD)
    catBeltRight.spin(FORWARD)
    for _ in range(3 * 100):  # 3 seconds @ 10ms/loop
        if catEye.isObjectVisible(): break
        wait(10, MSEC)
    # TODO: Check if we still need/want this. Tune it to new Gen3 bot?
    # Spinning the catapult a little more because sensor placement can't go lower
    catBeltRight.spin_for(FORWARD, 10, DEGREES, wait = False)
    catBeltLeft.spin_for(FORWARD, 10, DEGREES)
    stopCatAndBelt()

def releaseCat(cancelRewind = None): # Down Button
    releaseHug()
    catBeltRight.spin_for(FORWARD, 180, DEGREES, wait=False)
    catBeltLeft.spin_for(FORWARD, 180, DEGREES)
    # cancelWinding lets the caller of releaseCat() know
    # if winding should be cancelled (keeps tension off rubber bands)
    if (cancelRewind is None or not cancelRewind()): windCat()

def releaseHug(stop: bool = True):
    if stop: stopCatAndBelt()
    ballHugger.pump_on()
    ballHugger.extend(CylinderType.CYLINDER1)
    ballHugger.extend(CylinderType.CYLINDER2)

def hugBall():
    ballHugger.pump_on()
    ballHugger.retract(CylinderType.CYLINDER1)
    ballHugger.retract(CylinderType.CYLINDER2)

def stopAll():
    stopCatAndBelt()
    releaseHug(stop=True)
    if not intakeRunning: ballHugger.pump_off()  # Stop TWICE to shut off the pump
    stopIntake(HOLD)

def onCatSeen():
    pass

def onCatLost():
    pass

# Broadcasters
buttBumperPressed: Event = Event(onButtBumperPressed)
buttBumperReleased: Event = Event(onButtBumperReleased)

def checkEyes():
    intakeEye.setCallbacks(onIntakeBallSeen, onIntakeBallLost)
    topEye.setCallbacks(onTopBallSeen, onTopBallLost)
    catEye.setCallbacks(onCatSeen, onCatLost)
    while True: # Loop forever in a thread (like "when started" in Vex Blocks)
        intakeEye.look()
        topEye.look()
        catEye.look()
        wait(10, MSEC)

sensorThread = Thread(checkEyes)

MODES = ["CALIBRATE", "4SWITCHES", "NEAR_GOAL"]
MODE_COLORS = [Color.CYAN, Color.YELLOW_GREEN, Color.BLUE]
MODE_PEN_COLORS = [Color.BLACK, Color.BLACK, Color.WHITE]



def setupSelector():
    brain.buttonRight.pressed(onBrainButtonRight)
    brain.buttonLeft.pressed(onBrainButtonLeft)
    brain.buttonCheck.pressed(onBrainButtonCheck)

isAutoRunning = False
isCalibrated = False
modeNumber = 0
cancelCalibration = False

def onBrainButtonCheck():
    global isAutoRunning
    global isCalibrated
    global modeNumber

    if isAutoRunning:
        print("Already running")
    elif not isCalibrated and modeNumber > 0:  # Red block has no calibration
        if setupAutoDriveTrain():
            print("Ready!")
        else:
            print("Try again?")
    else:
        isAutoRunning = True
        if modeNumber == 0:
            runCalibrate()
        elif modeNumber == 1:
            run4Switches()
        elif modeNumber == 2:
            runNearGoal()
        isAutoRunning = False
        print("Done")

def onBrainButtonRight():
    applyMode(modeNumber + 1)

def onBrainButtonLeft():
    applyMode(modeNumber - 1)

def applyMode( newMode):
    global cancelCalibration
    if inertial.is_calibrating():
        cancelCalibration = False
    if isAutoRunning:
        print("Running auto already")
    else:
        modeNumber = newMode % len(MODES)
        fillScreen(MODE_COLORS[modeNumber], MODE_PEN_COLORS[modeNumber])
        print(MODES[modeNumber])

def fillScreen(screenColor, penColor):
    screenColor = screenColor
    penColor = penColor
    brain.screen.clear_screen()
    brain.screen.set_fill_color(screenColor)
    brain.screen.set_pen_color(screenColor)
    brain.screen.draw_rectangle(0, 0, 170, 100, screenColor)
    brain.screen.set_pen_color(penColor)
    brain.screen.set_font(FontType.MONO20)
    brain.screen.set_cursor(1, 1)
    
def print( message):
    brain.screen.set_fill_color(screenColor)
    brain.screen.set_pen_color(penColor)
    brain.screen.print(message)
    brain.screen.new_line()

def setupAutoDriveTrain(calibrate=True):
    # Use DriveTrain in autonomous. Easier to do turns.
    # Last updated on Nov 14, 2023:
    # Track width: 7-7/8 inches (7.875)
    # Wheel base : 6-1/2 inches (6.5)

    if not DriveTrain:
        driveTrain = DriveTrain(wheelLeft,
                                        wheelRight,
                                        wheelTravel= 145,
                                        trackWidth=246,
                                        wheelBase=200,
                                        units=DistanceUnits.MM,
                                        externalGearRatio=2)  # TODO: Is this correct?
        if calibrate:
            windCat()
            return calibrate
        return True

def calibrate():
    print("Calibrating...")
    inertial.calibrate()
    countdown = 3000/50  
    while (inertial.is_calibrating()
            and countdown > 0
            and not cancelCalibration):
        wait(50, MSEC)
        countdown = countdown - 1
    if cancelCalibration:   
        print("Cancelled Calibration!")
        return False
    elif countdown > 0 and not inertial.is_calibrating():
        windCat()
        print("Calibrated")
        brain.play_sound(SoundType.TADA)
        isCalibrated = True
        return True
    else:
        stopAll()
        print("FAILED Calibration")
        brain.play_sound(SoundType.POWER_DOWN)
        return False

# Use negativ4 velocity to go the opposite way
def goTurn90( velocityPercent: float, timeoutSecs: float = 0.0):
    leftDir = REVERSE if velocityPercent > 0 else FORWARD
    rightDir = FORWARD if velocityPercent > 0 else REVERSE
    wheelLeft.set_velocity(abs(velocityPercent), PERCENT)
    wheelRight.set_velocity(abs(velocityPercent), PERCENT)
    wheelLeft.set_max_torque(100, PERCENT)
    wheelRight.set_max_torque(100, PERCENT)
    if timeoutSecs > 0.0:
        wheelLeft.set_timeout(timeoutSecs, SECONDS)
        wheelRight.set_timeout(timeoutSecs, SECONDS)
    wheelLeft.spin_for(leftDir,0.44, TURNS, wait=False)
    wheelRight.spin_for(rightDir, 0.44, TURNS, wait=True)
    wheelLeft.stop(BRAKE)
    wheelRight.stop(BRAKE)
    brain.play_sound(SoundType.TADA)
    print("{:4.2f}".format(inertial.heading()))

def goTurn(
            velocity: float,
            angle: float,
            timeoutSecs: int = 0):
    # Angle is absolute, relative to the calibrated heading of 0-deg 
    while True:
        h = inertial.heading()
        if h > 180:
            h -= 360   # Convert larger angles to smaller angles by going the other way.
        error = angle - h  # Can be positive or negative depending on which way.
        if abs(error) < 0.1:
            print("All done. h={:4.2f}".format(h))
            brain.play_sound(SoundType.FILLUP)
            break
        
        # Taper the final 20-degrees linearly (each wheel halves the v)
        turnVelocity = velocity/2
        if abs(error) <= 30:
            print("TAPERING! error={:4.2f}".format(error))
            turnVelocity = ((error/30) * velocity)/2
        # When velocity is TOO slow, the bot won't move
        if abs(turnVelocity) < 8:
            turnVelocity = 8 if turnVelocity > 0 else -8
        print("h={:4.2f} e={:4.2f} adj={:4.2f}".format(h, error, turnVelocity))
        
        if angle < 0:
            wheelLeft.set_velocity(-turnVelocity)
            wheelRight.set_velocity(turnVelocity)
        else:
            wheelLeft.set_velocity(turnVelocity)
            wheelRight.set_velocity(-turnVelocity)

        wait(10, MSEC)
    wheelLeft.stop(HOLD)
    wheelRight.stop(HOLD)

    # Debugging
    n = 0
    while True:
        d = inertial.heading()
        print("Headig: {:4.2f}".format(d))
        wait(1, SECONDS)
        n += 1
        if n > 10:
            break

def convertHeadingToYaw(heading):
        y = heading
        if heading > 180:
            y = heading - 360
        return y

def clamp(value: float, minValue: float, maxValue: float):
    return max(minValue, min(maxValue, value))

def clampDelta(value: float, center: float, delta: float):
    return clamp(value, center - delta, center + delta)

def getAngle():
    return inertial.rotation()

def resetMotors():
    wheelLeft.reset_position()
    wheelRight.reset_position()

def getMotorsRevolution():
    return (wheelLeft.position(RotationUnits.REV) + wheelRight.position(RotationUnits.REV)) / 2.0

def setMotorSpeeds(leftSpeed: float, rightSpeed: float):
    wheelLeft.spin(DirectionType.FORWARD, leftSpeed, PERCENT)
    wheelRight.spin(DirectionType.FORWARD, rightSpeed, PERCENT)

def goCurve(targetAngle: float,
            targetSpeed: float,
            targetRevolutions: float,
            maxAcceleration: float = 150.0,
            maxAngleSpeed: float = 50.0,
            maxAngleAcceleration: float = 300.0,
            angleTolerance: float = 1.0,
            kP: float = 1.0,
            deltaTime: float = 20e-3):
    def limitAcceleration(desired: float, current: float, maxAcceleration: float):
        return clampDelta(desired, current, maxAcceleration*deltaTime)
    
    lastSpeed = 0.0
    lastCorrection = 0.0
    resetMotors()
    
    while True:
        currentAngle = getAngle()
        error = currentAngle - targetAngle
        correction = kP * error
        correction = clamp(correction, -maxAngleSpeed, maxAngleSpeed)
        correction = limitAcceleration(correction, lastCorrection, maxAngleAcceleration)
        achievedRevolutions = getMotorsRevolution() >= targetRevolutions
        requiredSpeed = 0.0 if achievedRevolutions else targetSpeed
        desiredSpeed = limitAcceleration(requiredSpeed, lastSpeed, maxAcceleration)
        leftSpeed = clamp(desiredSpeed - correction, -100.0, 100.0)
        rightSpeed = clamp(desiredSpeed + correction, -100.0, 100.0)
        setMotorSpeeds(leftSpeed, rightSpeed)
        lastSpeed = desiredSpeed
        lastCorrection = correction
        achievedDesiredAngle = abs(error) < angleTolerance
        if desiredSpeed == 0.0 and achievedDesiredAngle:
            break
        wait(deltaTime, SECONDS)

def goStraight(
                inches: float,
                velocity: float,
                timeoutSecs: int = 0,
                requiredYaw: float = 360, # Default of 360 means ignore
                wheelDiameterMM: int = 200,
                driveGearRatio: float = 0.5,
                ):
    cancelGoStraight = False
    taperTurns = 0.75     # Turns remaining on wheels before start tapering
    convertINtoMM = 25.4
    wheelDiameterMM = 200
    distanceMM = inches * convertINtoMM
    turnsNeeded = (distanceMM / wheelDiameterMM) * driveGearRatio

    wheelLeft.set_velocity(velocity, PERCENT)
    wheelRight.set_velocity(velocity, PERCENT)
    wheelLeft.set_position(0, RotationUnits.REV)
    wheelRight.set_position(0, RotationUnits.REV)
    wheelLeft.spin(FORWARD)
    wheelRight.spin(FORWARD)
    # Force the robot to get to a certain angle heading
    if abs(requiredYaw) <= 180:
        baseYaw = requiredYaw
    else:
        baseYaw = convertHeadingToYaw(inertial.heading()) # Where did we start?
    h = 0 
    damper = 1.0

    print("***********************")
    startTime = time.time()
    while not cancelGoStraight:
        i = convertHeadingToYaw(inertial.heading())
        d = i - baseYaw
        if abs(d) > 0.1: # Ignore small changes
            # Don't change velocity by more than 50% on either wheel
            # Adjust in proportion to delta of the 45 degrees
            adjustment = (50 * d)/90
        else:
            adjustment = 0

        # Taper speed as we approach our target # of turns
        leftPos = wheelLeft.position(RotationUnits.REV)
        rightPos = wheelRight.position(RotationUnits.REV)
        turns = (leftPos + rightPos) / 2  # Take an average...why not?
        remaining = turnsNeeded - abs(turns)
        leftVelocity = 0
        rightVelocity = 0
        if remaining <= 0.0:
            velocity = 0
            adjustment = 0
        elif remaining <= taperTurns:   # Set new velocity when not many turns are left
            damper = (remaining / taperTurns) if remaining >= 0 else 0.0
            leftVelocity = (velocity * damper)
            rightVelocity = (velocity * damper)
            if (abs(leftVelocity) < 20): # velocity too low doesn't work well
                leftVelocity = 20 if velocity > 0 else -20
            if (abs(rightVelocity) < 20): # velocity too low doesn't work well
                rightVelocity = 20 if velocity > 0 else -20
            leftVelocity -= adjustment
            rightVelocity += adjustment
        else:
            leftVelocity = velocity - adjustment
            rightVelocity = velocity + adjustment
            
        wheelLeft.set_velocity(leftVelocity)
        wheelRight.set_velocity(rightVelocity)

        print("{:4.1f}, {:4.1f}: h={:4.1f} d={:4.1f} a={:4.1f} damper={:4.1f} v1={:4.1f} v2={:4.1f}".format(leftPos, rightPos, h, d, adjustment, damper, leftVelocity, rightVelocity))
        if (abs(turns) >= turnsNeeded):
            print("DONE: turns={:4.1f} needed={:4.1f} error={:4.1f}".format(turns, turnsNeeded, turns - turnsNeeded))
            break
        wait(10, MSEC)

        # Check timeout
        if (timeoutSecs > 0 and ((time.time() - startTime) >= timeoutSecs)):
            brain.play_sound(SoundType.DOOR_CLOSE)
            print("TIMEOUT!")
            break

    wheelLeft.set_velocity(0)
    wheelRight.set_velocity(0)
    wheelLeft.stop()
    wheelRight.stop()
    if cancelGoStraight:
        print("CANCELLED")
        cancelGoStraight = False  # Reset this

def run():
    setup()
    fillScreen(Color.BLUE_VIOLET, Color.WHITE)
    print("Extreme")
    print("Axolotls!")
    
    # Wait for someone to select a program to run

def finishCheckpoint():
    brain.play_sound(SoundType.FILLUP)

def finishRun():        
    brain.play_sound(SoundType.TADA)

def runCalibrate():
    setupAutoDriveTrain(calibrate=False)
    windCat()
    calibrate()

def autoLoop():
    startIntake()
    goStraight(55, 65, timeoutSecs=5, requiredYaw=-90)
    goStraight(60, -65, timeoutSecs=5, requiredYaw=-90)
    goStraight(10, -15, timeoutSecs=5, requiredYaw=-90)
    #intake.stop(COAST)
    wait(100, MSEC)
    releaseCat()
    wait(100, MSEC)
    releaseCat()
    windCat()

def run4Switches():
    pass

def runNearGoal():
    windCat()
    startIntake()
    goStraight(10, 40, timeoutSecs=5,requiredYaw=0)
    goTurn90(25, 4) # Turns to face goal
    goStraight(40, -50, timeoutSecs=4, requiredYaw=-90) # go back
    #goStraight(20, 40, timeoutSecs=3, requiredYaw=-90) #collects ball
    goStraight(35, -50, timeoutSecs=5, requiredYaw=-90) #Drives to goal
    #intake.stop(COAST)
    wait(1000,MSEC)
    releaseCat()
    wait(100,MSEC)
    releaseCat()
    windCat()
    for i in range(5):
        autoLoop()