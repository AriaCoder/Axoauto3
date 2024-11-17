# AXOBOTL Python Code
# Extreme Axolotls Robotics team 4028X for 2023-2024 VEX IQ Full Volume Challenge
from vex import *
import time


class Bot:
    MODES = ["CALIBRATE", "4SWITCHES", "NEAR_GOAL", "REPEAT"]
    MODE_COLORS = [Color.CYAN, Color.YELLOW_GREEN, Color.BLUE, Color.VIOLET]
    MODE_PEN_COLORS = [Color.BLACK, Color.BLACK, Color.WHITE, Color. WHITE]

    def __init__(self):
        self.isAutoRunning = False
        self.cancelGoStraight = False
        self.modeNumber = -1
        self.isCalibrated = False
        self.cancelCalibration = False
        self.screenColor = Color.BLACK
        self.penColor = Color.WHITE

    def setup(self):
        self.brain = Brain()
        self.inertial = Inertial()
        self.setupPortMappings()
        self.setupDrive()
        self.setupIntake()
        self.setupCatapult()
        self.setupSelector()
        self.setupCatapultBumper()
        #self.setupHealthLed()
        #self.runCurrentModeNumber()

    def setupPortMappings(self):
        self.motorLeft = Motor(Ports.PORT7,1,True)
        self.motorRight = Motor(Ports.PORT12,1, False)
        self.intakeLeft = Motor(Ports.PORT1,1,True)
        self.intakeRight = Motor(Ports.PORT4)
        self.healthLedLeft = Touchled(Ports.PORT10)
        self.catapultRight = Motor(Ports.PORT11)
        self.catapultLeft = Motor(Ports.PORT3, True)
        self.healthLedRight = Touchled(Ports.PORT9)
        self.catapultSensor = Distance(Ports. PORT2)
        self.catapultBumper = Bumper(Ports.PORT8)
        self.driveTrain = None  # Default is MANUAL mode, no driveTrain

    def onCatapultBumperPressed(self):
        self.cancelGoStraight = True

    def setupHealthled(self):
        color = Color.RED
        capacity = self.brain.battery.capacity()
        if capacity > 95:
            color = Color.BLUE
        elif capacity > 90:
            color = Color.GREEN
        elif capacity > 80:
            color = Color.YELLOW_ORANGE
        else:
            self.print("Battery too low for auto")
            color = Color.RED
        self.healthLedRight.set_color(color)

    #def setupHealthLed(self):
     #   self.healthLedRight.pressed(self.onHealthLedRightPressed)

    #def onHealthLedRightPressed(self):
      #  self.runCurrentModeNumber()

   # def runCurrentModeNumber(self):
      #   if self.modeFunction != None:
        #    f = self.modeFunction
         #   self.modeFunction = None  # Clear out the function before running it
        #    f()  # You're allowed to "run" a function variable
        #    self.print("Done")

    def setupIntake(self):
        self.intake = MotorGroup(self.intakeLeft, self.intakeRight)

    def startIntake(self):
        if not self.isCatapultDown():
            self.windCatapult()
        self.intake.spin(FORWARD, 100, PERCENT)

    def stopIntake(self):
        self.intake.stop()

    def setupCatapultBumper(self):
        self.catapultBumper.pressed(self.onCatapultBumperPressed)

    def setupCatapult(self):
        self.catapultLeft.set_velocity(100, PERCENT)
        self.catapultRight.set_velocity(100, PERCENT)
        self.catapultLeft.set_max_torque(100, PERCENT)
        self.catapultRight.set_max_torque(100, PERCENT)
        self.catapultLeft.set_stopping(HOLD)
        self.catapultRight.set_stopping(HOLD)

    def windCatapult(self):  # Up Button
        while not self.isCatapultDown():
            self.catapultRight.spin(FORWARD)
            self.catapultLeft.spin(FORWARD)
            wait(10, MSEC)
        # Spinning the catapult a little more because sensor placement can't go lower
      #  self.catapultRight.spin_for(FORWARD, 60, DEGREES, wait = False)
    #    self.catapultLeft.spin_for(FORWARD, 60, DEGREES)
        self.catapultRight.stop(HOLD)
        self.catapultLeft.stop(HOLD)

    def isCatapultDown(self):
        return self.catapultSensor.object_distance(MM) < 30

    def releaseCatapult(self): # Down Button
        if self.isCatapultDown:
            self.catapultLeft.spin_for(FORWARD, 180, DEGREES, wait = False)
            self.catapultRight.spin_for(FORWARD, 180, DEGREES)
            self.isCatapultDown()
            self.windCatapult()

    def setupSelector(self):
        self.brain.buttonRight.pressed(self.onBrainButtonRight)
        self.brain.buttonLeft.pressed(self.onBrainButtonLeft)
        self.brain.buttonCheck.pressed(self.onBrainButtonCheck)

    def onBrainButtonCheck(self):
        if self.isAutoRunning:
            self.print("Already running")
        elif not self.isCalibrated and self.modeNumber > 0:  # Red block has no calibration
            if self.setupAutoDriveTrain():
                self.print("Ready!")
            else:
                self.print("Try again?")
        else:
            self.isAutoRunning = True
            if self.modeNumber == 0:
                self.runCalibrate()
            elif self.modeNumber == 1:
                self.run4Switches()
            elif self.modeNumber == 2:
                self.runNearGoal()
            elif self.modeNumber == 3:
                self.runRepeat()
            self.isAutoRunning = False
            self.print("Done")

    def onBrainButtonRight(self):
        self.applyMode(self.modeNumber + 1)

    def onBrainButtonLeft(self):
        self.applyMode(self.modeNumber - 1)

    def applyMode(self, newMode):
        if self.inertial.is_calibrating():
            self.cancelCalibration = False
        if self.isAutoRunning:
            self.print("Running auto already")
        else:
            self.modeNumber = newMode % len(Bot.MODES)
            self.fillScreen(Bot.MODE_COLORS[self.modeNumber], Bot.MODE_PEN_COLORS[self.modeNumber])
            self.print(Bot.MODES[self.modeNumber])

    def fillScreen(self, screenColor, penColor):
        self.screenColor = screenColor
        self.penColor = penColor
        self.brain.screen.clear_screen()
        self.brain.screen.set_fill_color(screenColor)
        self.brain.screen.set_pen_color(screenColor)
        self.brain.screen.draw_rectangle(0, 0, 170, 100, screenColor)
        self.brain.screen.set_pen_color(penColor)
        self.brain.screen.set_font(FontType.MONO20)
        self.brain.screen.set_cursor(1, 1)
        
    def print(self, message):
        self.brain.screen.set_fill_color(self.screenColor)
        self.brain.screen.set_pen_color(self.penColor)
        self.brain.screen.print(message)
        self.brain.screen.new_line()

    def setupDrive(self):
        self.motorLeft.set_velocity(0, PERCENT)
        self.motorLeft.set_max_torque(100, PERCENT)
        self.motorLeft.spin(REVERSE)
        self.motorRight.set_velocity(0, PERCENT)
        self.motorRight.set_max_torque(100, PERCENT)
        self.motorRight.spin(REVERSE)

    def stopAll(self):
        if self.driveTrain:
            self.driveTrain.stop(HOLD)
        self.intakeLeft.stop(COAST)
        self.intakeRight.stop(COAST)
        self.catapultLeft.stop(COAST)
        self.catapultRight.stop(COAST)

    def setupAutoDriveTrain(self, calibrate=True):
        # Use DriveTrain in autonomous. Easier to do turns.
        # Last updated on Nov 14, 2023:
        # Track width: 7-7/8 inches (7.875)
        # Wheel base : 6-1/2 inches (6.5)

        if not self.driveTrain:
            self.driveTrain = DriveTrain(self.motorLeft,
                                            self.motorRight,
                                            wheelTravel= 145,
                                            trackWidth=246,
                                            wheelBase=200,
                                            units=DistanceUnits.MM,
                                            externalGearRatio=2)  # TODO: Is this correct?
            if calibrate:
                self.windCatapult()
                return self.calibrate()
            return True

    def calibrate(self):
        self.print("Calibrating...")
        self.inertial.calibrate()
        countdown = 3000/50  
        while (self.inertial.is_calibrating()
                and countdown > 0
                and not self.cancelCalibration):
            wait(50, MSEC)
            countdown = countdown - 1
        if self.cancelCalibration:   
            self.print("Cancelled Calibration!")
            return False
        elif countdown > 0 and not self.inertial.is_calibrating():
            self.windCatapult()
            self.print("Calibrated")
            self.brain.play_sound(SoundType.TADA)
            self.isCalibrated = True
            return True
        else:
            self.stopAll()
            self.print("FAILED Calibration")
            self.brain.play_sound(SoundType.POWER_DOWN)
            return False

    # Use negativ4 velocity to go the opposite way
    def goTurn90(self, velocityPercent: float, timeoutSecs: float = 0.0):
        leftDir = REVERSE if velocityPercent > 0 else FORWARD
        rightDir = FORWARD if velocityPercent > 0 else REVERSE
        self.motorLeft.set_velocity(abs(velocityPercent), PERCENT)
        self.motorRight.set_velocity(abs(velocityPercent), PERCENT)
        self.motorLeft.set_max_torque(100, PERCENT)
        self.motorRight.set_max_torque(100, PERCENT)
        if timeoutSecs > 0.0:
            self.motorLeft.set_timeout(timeoutSecs, SECONDS)
            self.motorRight.set_timeout(timeoutSecs, SECONDS)
        self.motorLeft.spin_for(leftDir,0.44, TURNS, wait=False)
        self.motorRight.spin_for(rightDir, 0.44, TURNS, wait=True)
        self.motorLeft.stop(BRAKE)
        self.motorRight.stop(BRAKE)
        self.brain.play_sound(SoundType.TADA)
        print("{:4.2f}".format(self.inertial.heading()))

    def goTurn(self,
                velocity: float,
                angle: float,
                timeoutSecs: int = 0):
        # Angle is absolute, relative to the calibrated heading of 0-deg 
        while True:
            h = self.inertial.heading()
            if h > 180:
                h -= 360   # Convert larger angles to smaller angles by going the other way.
            error = angle - h  # Can be positive or negative depending on which way.
            if abs(error) < 0.1:
                print("All done. h={:4.2f}".format(h))
                self.brain.play_sound(SoundType.FILLUP)
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
                self.motorLeft.set_velocity(-turnVelocity)
                self.motorRight.set_velocity(turnVelocity)
            else:
                self.motorLeft.set_velocity(turnVelocity)
                self.motorRight.set_velocity(-turnVelocity)

            wait(10, MSEC)
        self.motorLeft.stop(HOLD)
        self.motorRight.stop(HOLD)

        # Debugging
        n = 0
        while True:
            d = self.inertial.heading()
            print("Headig: {:4.2f}".format(d))
            wait(1, SECONDS)
            n += 1
            if n > 10:
                break

    def convertHeadingToYaw(self, heading):
            y = heading
            if heading > 180:
                y = heading - 360
            return y

    def goStraight(self,
                   inches: float,
                   velocity: float,
                   timeoutSecs: int = 0,
                   requiredYaw: float = 360, # Default of 360 means ignore
                   wheelDiameterMM: int = 200,
                   driveGearRatio: float = 0.5):
        taperTurns = 0.75     # Turns remaining on wheels before start tapering
        convertINtoMM = 25.4
        wheelDiameterMM = 200
        distanceMM = inches * convertINtoMM
        turnsNeeded = (distanceMM / wheelDiameterMM) * driveGearRatio

        self.motorLeft.set_velocity(velocity, PERCENT)
        self.motorRight.set_velocity(velocity, PERCENT)
        self.motorLeft.set_position(0, RotationUnits.REV)
        self.motorRight.set_position(0, RotationUnits.REV)
        self.motorLeft.spin(FORWARD)
        self.motorRight.spin(FORWARD)
        # Force the robot to get to a certain angle heading
        if abs(requiredYaw) <= 180:
            baseYaw = requiredYaw
        else:
            baseYaw = self.convertHeadingToYaw(self.inertial.heading()) # Where did we start?
        h = 0 
        damper = 1.0

        print("***********************")
        startTime = time.time()
        while not self.cancelGoStraight:
            i = self.convertHeadingToYaw(self.inertial.heading())
            d = i - baseYaw
            if abs(d) > 0.1: # Ignore small changes
                # Don't change velocity by more than 50% on either wheel
                # Adjust in proportion to delta of the 45 degrees
                adjustment = (50 * d)/90
            else:
                adjustment = 0

            # Taper speed as we approach our target # of turns
            leftPos = self.motorLeft.position(RotationUnits.REV)
            rightPos = self.motorRight.position(RotationUnits.REV)
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
                
            self.motorLeft.set_velocity(leftVelocity)
            self.motorRight.set_velocity(rightVelocity)

            print("{:4.1f}, {:4.1f}: h={:4.1f} d={:4.1f} a={:4.1f} damper={:4.1f} v1={:4.1f} v2={:4.1f}".format(leftPos, rightPos, h, d, adjustment, damper, leftVelocity, rightVelocity))
            if (abs(turns) >= turnsNeeded):
                print("DONE: turns={:4.1f} needed={:4.1f} error={:4.1f}".format(turns, turnsNeeded, turns - turnsNeeded))
                break
            wait(10, MSEC)

            # Check timeout
            if (timeoutSecs > 0 and ((time.time() - startTime) >= timeoutSecs)):
                self.brain.play_sound(SoundType.DOOR_CLOSE)
                print("TIMEOUT!")
                break

        self.motorLeft.set_velocity(0)
        self.motorRight.set_velocity(0)
        self.motorLeft.stop()
        self.motorRight.stop()
        if self.cancelGoStraight:
            print("CANCELLED")
        self.cancelGoStraight = False  # Reset this

    def autoTurn(self, direction, angle, units=RotationUnits.DEG,
                 velocity=50, units_v:VelocityPercentUnits=VelocityUnits.PERCENT, wait=True,
                 timeoutSecs=100):
        if self.driveTrain is not None:
            if timeoutSecs != 100:
                self.driveTrain.set_timeout(timeoutSecs, TimeUnits.SECONDS)
            self.driveTrain.turn_for(direction, angle / 2, units, velocity, units_v, wait)
            if timeoutSecs != 100:  # Restore timeout for future driveTrain users
                self.driveTrain.set_timeout(100, TimeUnits.SECONDS)
   
    def run(self):
        self.setup()
        self.fillScreen(Color.BLUE_VIOLET, Color.WHITE)
        self.print("Extreme")
        self.print("Axolotls!")
        
        # Wait for someone to select a program to run

    def finishCheckpoint(self):
        self.brain.play_sound(SoundType.FILLUP)

    def finishRun(self):        
        self.brain.play_sound(SoundType.TADA)

    def runCalibrate(self):
        self.setupAutoDriveTrain(calibrate=False)
       # self.windCatapult()
        self.calibrate()

    def autoLoop(self):
        self.startIntake()
        self.goStraight(55, 65, timeoutSecs=5, requiredYaw=-90)
        self.goStraight(60, -65, timeoutSecs=5, requiredYaw=-90)
        self.goStraight(10, -15, timeoutSecs=5, requiredYaw=-90)
        self.intake.stop(COAST)
        wait(100, MSEC)
        self.releaseCatapult()
        wait(100, MSEC)
        self.releaseCatapult()
        self.windCatapult()

    def run4Switches(self):
        self.windCatapult()
        self.goStraight(10, 30, timeoutSecs=5,requiredYaw=0)
        self.goTurn90(20, 4) # Turns to face goal
        self.goStraight(40, -40, timeoutSecs=5, requiredYaw=-90) # go back
        self.startIntake()
        self.goStraight(20, 40, timeoutSecs=3, requiredYaw=-90) #collects ball
        self.goStraight(30, -60, timeoutSecs=5, requiredYaw=-90) #Drives to goal
        self.intake.stop(COAST)
        wait(1000,MSEC)
        self.releaseCatapult()
        wait(100,MSEC)
        self.releaseCatapult()
        self.windCatapult()
        self.startIntake()
        self.windCatapult()
        self.goStraight(30,60,timeoutSecs=1, requiredYaw=-90)
        self.goStraight(30, 60, timeoutSecs=3, requiredYaw=-90) #Away from goal
        self.goTurn90(-30,4)
        self.goStraight(47,60,timeoutSecs=2,requiredYaw=0)
        self.goTurn90(40, 4) # Turns to face goal
        self.goStraight(50, -40, timeoutSecs=5, requiredYaw=-90) #Drives to goal
        self.releaseCatapult()
        wait(100,MSEC)
        self.releaseCatapult()
        self.windCatapult()
        self.stopAll()
        self.goStraight(30, -100, timeoutSecs=2, requiredYaw=-90) # A little last push
        self.stopAll()

    def runNearGoal(self):
        self.windCatapult()
        self.startIntake()
        self.goStraight(10, 40, timeoutSecs=5,requiredYaw=0)
        self.goTurn90(25, 4) # Turns to face goal
        self.goStraight(40, -50, timeoutSecs=4, requiredYaw=-90) # go back
        #self.goStraight(20, 40, timeoutSecs=3, requiredYaw=-90) #collects ball
        self.goStraight(35, -50, timeoutSecs=5, requiredYaw=-90) #Drives to goal
        self.intake.stop(COAST)
        wait(1000,MSEC)
        self.releaseCatapult()
        wait(100,MSEC)
        self.releaseCatapult()
        self.windCatapult()
        for i in range(5):
          self.autoLoop()
        
   
# Where it all begins!    
bot = Bot()
bot.run()