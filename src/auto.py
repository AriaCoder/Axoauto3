# AXOBOTL Python Code
# Extreme Axolotls Robotics team 4028X for 2023-2024 VEX IQ Full Volume Challenge
from vex import *
import time


class Bot:
    MODES = ["CALIBRATE", "NEAR_GOAL", "FAR_GOAL", "REPEAT"]
    MODE_COLORS = [Color.CYAN, Color.YELLOW_GREEN, Color.BLUE, Color.VIOLET]
    MODE_PEN_COLORS = [Color.BLACK, Color.BLACK, Color.WHITE, Color. WHITE]

    def __init__(self):
        self.isAutoRunning = False
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
        self.releaseCatapult()

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


    def startIntake(self):
        self.intake = MotorGroup(self.intakeLeft,self.intakeRight)
        if self.isCatapultDown:
            self.intake.spin(FORWARD, 100, PERCENT)
        else:
            self.windCatapult()
            self.intake.spin(FORWARD, 100, PERCENT)


    def setupCatapultBumper(self):
        pass

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
            wait(200, MSEC)
 
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
                self.runNearGoal()
            elif self.modeNumber == 2:
                self.runFarGoal()
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
        penColor = Bot.MODE_PEN_COLORS[self.modeNumber]
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

    def goTurn(self,
                velocity: float,
                angle: float,
                timeoutSecs: int = 0):
        while True:
            h = self.inertial.heading()
            if h > 180:
                h -= 360   # Convert larger angles to smaller angles by going the other way.
            error = angle - h  # Can be positive or negative depending on which way.
            if abs(error) < 0.5:
                break
            adj = (error * 50) /180 # Capping to 50% - don't turn too much!
            sign = (error/abs(error))
            print("h={:4.2f} e={:4.2f} adj={:4.2f}".format(h, error, adj))
            self.motorLeft.set_velocity(sign*velocity)
            self.motorRight.set_velocity(-sign*velocity)
            wait(20, MSEC)
        self.motorLeft.stop(HOLD)
        self.motorRight.stop(HOLD)

    def convertHeadingToRotation(self, heading):
            # Map the 0-365 heading to -45 to 45 degrees range with a step function
            # The 45-degrees is arbitrary.
            r = 0
            if heading > 315:
                r = heading - 360
            elif heading > 180:
                r = -45  # Don't allow angles > 45-deg either way
            elif heading > 45:
                r = 45
            else:
                r = heading
            return r

    def goStraight(self,
                   velocity: float,
                   inches: float,
                   timeoutSecs: int = 0,
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
        baseRotation = self.convertHeadingToRotation(self.inertial.heading()) # Where did we start?
        h = 0 
        damper = 1.0

        startTime = time.time()
        while True:
            i = self.convertHeadingToRotation(self.inertial.heading())
            d = i - baseRotation
            if abs(d) > 0.1: # Ignore small changes
                # Don't change velocity by more than 50% on either wheel
                # Adjust in proportion to delta of the 45 degrees
                adjustment = (50 * d)/45
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
                print("TIMEOUT!")
                break

        self.motorLeft.set_velocity(0)
        self.motorRight.set_velocity(0)
        self.motorLeft.stop()
        self.motorRight.stop()

    def autoDrive(self, direction, distance, units=DistanceUnits.MM,
                  velocity=100, units_v:VelocityPercentUnits=VelocityUnits.RPM,
                  wait=True, timeoutSecs=100):
        if self.driveTrain is not None:
            if timeoutSecs != 100:
                self.driveTrain.set_timeout(timeoutSecs, TimeUnits.SECONDS)
            self.driveTrain.drive_for(direction, distance, units, velocity, units_v, wait)
            if timeoutSecs != 100:  # Restore timeout for future driveTrain users
                self.driveTrain.set_timeout(100, TimeUnits.SECONDS)


    def autoTurn(self, direction, angle, units=RotationUnits.DEG,
                 velocity=50, units_v:VelocityPercentUnits=VelocityUnits.PERCENT, wait=True,
                 timeoutSecs=100):
        if self.driveTrain is not None:
            if timeoutSecs != 100:
                self.driveTrain.set_timeout(timeoutSecs, TimeUnits.SECONDS)
            self.driveTrain.turn_for(direction, angle / 2, units, velocity, units_v, wait)
            if timeoutSecs != 100:  # Restore timeout for future driveTrain users
                self.driveTrain.set_timeout(100, TimeUnits.SECONDS)

   # def autoHdrive(self, direction, distance, units=DistanceUnits.MM, velocity=100,
    #               units_v:VelocityPercentUnits=VelocityUnits.RPM, wait=True, timeoutSecs=100):
     #    if self.wheelCenter is not None:
      #      if not self.isCalibrated:
       #         self.calibrate()
       #     if timeoutSecs != 100:
        #        self.wheelCenter.set_timeout(timeoutSecs, TimeUnits.SECONDS)
        #    # Calculate spins
         #   spins = distance/2/200
         #   if units == DistanceUnits.MM:
         #       gearRatio = 2
          #      #wheelDiameterMM = 63.5
          #     spins = (distance/gearRatio)/200

              #  self.brain.play_sound(SoundType.TADA)
               # self.brain.screen.clear_screen()
               # self.print(spins)

                #self.wheelCenter.spin_for(direction, spins, TURNS, velocity, units_v, wait)
            #if timeoutSecs != 100:  # Restore timeout for future driveTrain users
            #    self.wheelCenter.set_timeout(100, TimeUnits.SECONDS)

    def autoArc(self, headingTarget: float, leftVelocityPercent: int, rightVelocityPercent: int, timeoutSecs=100):
        if timeoutSecs != 100:
            self.motorLeft.set_timeout(timeoutSecs)
            self.motorRight.set_timeout(timeoutSecs)
        self.motorLeft.spin(FORWARD, leftVelocityPercent, PERCENT)
        self.motorRight.spin(FORWARD, rightVelocityPercent, PERCENT)
        
        # TODO: Bail out based on timeout
        lastHeading = 0
        sameHeadings = 0
        while True:  # Wait to complete to arc
            heading = self.inertial.heading()
            print(heading)
            error = 5
            if (heading > (headingTarget - error) and heading < (headingTarget + error)):
                break
            if heading == lastHeading:
                sameHeadings += 1
            else:
                sameHeadings = 0
            if sameHeadings > 5:  # Stuck 
                break
            lastHeading = heading
            sleep(100, MSEC)

        self.motorLeft.stop(COAST)
        self.motorRight.stop(COAST)

        if timeoutSecs != 100:  # Restore old value?
            self.motorLeft.set_timeout(100)
            self.motorRight.set_timeout(100)
        
    # TODO: Add a parameter for green vs. purple blocks?
   
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

    def runNearGoal(self):
        self.windCatapult()
        self.goStraight(48, 20, timeoutSecs=2)
        self.autoTurn(LEFT, 90, DEGREES, 25, PERCENT) # Turns to face goal
        self.goStraight(-60, 20, timeoutSecs=2) #goes back
        self.goStraight(-60, 20, timeoutSecs=2)
        self.startIntake()
        self.goStraight(50, 15, timeoutSecs=2) #collects ball
        self.goStraight(-60, 60, timeoutSecs=1) #Drives to goal
        self.intake.stop(HOLD)
        #self.autoTurn(LEFT, 15, DEGREES, 50, PERCENT, timeoutSecs=2)#Wiggles in the goal
        self.goStraight(-100, 40, timeoutSecs=2)
        self.releaseCatapult()
        
        return
        self.autoDrive(REVERSE, 35, INCHES, 100, PERCENT, wait=True, timeoutSecs=2)
        self.releaseCatapult()
        self.autoDrive(FORWARD, 25, INCHES, 100, PERCENT, wait=True)  # Return home
        self.autoDrive( REVERSE, 8, INCHES, 100, PERCENT)
        self.catapultLeft.spin(FORWARD, 100, PERCENT)
        self.catapultRight.spin(FORWARD, 100, PERCENT)


    def runFarGoal(self):
        self.brain.screen.print("wrong goal!")
        self.startIntake()
        self.autoDrive(FORWARD, 360, MM, 45, PERCENT)
        self.autoTurn(LEFT, 2, DEGREES, 100, PERCENT, timeoutSecs=2)
        self.autoDrive(REVERSE, 260, MM, 35, PERCENT)
    
    def runRepeat(self):
        #self.intake.spin(REVERSE, 100, PERCENT)
        self.autoDrive(FORWARD, 350, MM, 25,PERCENT)
        self.autoDrive(REVERSE, 350, MM, 50, PERCENT)
        self.autoTurn(LEFT, 52, DEGREES, 100 , PERCENT)
        self.autoDrive(REVERSE, 350, MM, 100, PERCENT, timeoutSecs=3)
        self.stopAll()
       


        
# Where it all begins!    
bot = Bot()
bot.run()