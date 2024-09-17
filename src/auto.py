# AXOBOTL Python Code
# Extreme Axolotls Robotics team 4028X for 2023-2024 VEX IQ Full Volume Challenge
from vex import *


class Bot:
    MODES = ["NEAR_GOAL", "FAR_GOAL", "REPEAT"]
    MODE_COLORS = [Color.YELLOW_GREEN, Color.BLUE, Color.VIOLET]
    MODE_PEN_COLORS = [Color.BLACK, Color.WHITE, Color. WHITE]

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
        self.setupIntake()
        self.setupCatapult()
        self.setupSelector()

    def setupPortMappings(self):
        self.motorLeft = Motor(Ports.PORT7,1,True)
        self.motorRight = Motor(Ports.PORT12,1, False)
        self.intakeMotor = Motor(Ports.PORT1,1,True)
        self.catapultLeft = Motor(Ports.PORT3)
        self.catapultRight = Motor(Ports.PORT11)
        self.hDriveMotor = Motor(Ports.PORT9)
        self.startAuto = Touchled(Ports.PORT10)
        self.driveTrain = None  # Default is MANUAL mode, no driveTrain

    def setupIntake(self):
        self.intake = MotorGroup(self.intakeMotor)
        self.intake.set_velocity(100, PERCENT)

    def setupCatapult(self):
        self.catapult = MotorGroup(self.catapultLeft, self.catapultRight)
        self.catapult.set_velocity(100, PERCENT)

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
                self.runNearGoal()
            elif self.modeNumber == 1:
                self.runFarGoal()
            elif self.modeNumber == 2:
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

    def startIntake(self):
        self.intake.spin(REVERSE, 100, PERCENT)

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
        self.intake.stop(COAST)
        self.catapult.stop(COAST)

   # def checkHealth(self):
        #Copied from our code for Slapshot 2022-23 season
      #      color = Color.RED
   # capacity = self.brain.battery.capacity()
    #if capacity > 95:
     #       color = Color.BLUE
    #elif capacity > 85:
    #        color = Color.GREEN
   # elif capacity > 81:
    #        color = Color.ORANGE
    #else:
    #        self.print("Battery level is too low for auton")
     #       color = Color.RED
      #  self.healthLed.set_color(color

    def setupAutoDriveTrain(self, calibrate=True):
        # Use DriveTrain in autonomous. Easier to do turns.
        # Last updated on Nov 14, 2023:
        # Track width: 7-7/8 inches (7.875)
        # Wheel base : 6-1/2 inches (6.5)

        if not self.driveTrain:
            self.driveTrain = DriveTrain(self.motorLeft,
                                            self.motorRight,
                                            wheelTravel=200,
                                            trackWidth=200.025,
                                            wheelBase=165.1,
                                            units=DistanceUnits.MM,
                                            externalGearRatio=1)  # TODO: Is this correct?
            if calibrate:
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
            self.print("Calibrated")
            self.brain.play_sound(SoundType.TADA)
            self.isCalibrated = True
            return True
        else:
            self.stopAll()
            self.print("FAILED Calibration")
            self.brain.play_sound(SoundType.POWER_DOWN)
            return False

    def autoDrive(self, direction, distance, units=DistanceUnits.IN,
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

        self.motorLeft.stop(BRAKE)
        self.motorRight.stop(BRAKE)

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

    def runNearGoal(self):
        self.setupAutoDriveTrain(calibrate=False)
        self.intake.spin(FORWARD, 100, PERCENT)
        self.autoDrive(FORWARD, 500, MM, 100, PERCENT, wait=True, timeoutSecs=6)
        self.autoDrive(REVERSE, 500, MM, 100, PERCENT, wait=True)  # Return home


    def runFarGoal(self):
        self.startIntake()
        self.autoDrive(FORWARD, 360, MM, 45, PERCENT)
        self.autoTurn(LEFT, 2, DEGREES, 100, PERCENT, timeoutSecs=2)
        self.autoDrive(REVERSE, 260, MM, 35, PERCENT)
    
    def runRepeat(self):
        self.intake.spin(REVERSE, 100, PERCENT)
        self.autoDrive(FORWARD, 350, MM, 25,PERCENT)
        self.autoDrive(REVERSE, 350, MM, 50, PERCENT)
        self.autoTurn(LEFT, 52, DEGREES, 100 , PERCENT)
        self.autoDrive(REVERSE, 350, MM, 100, PERCENT, timeoutSecs=3)
        self.stopAll()
       


        
# Where it all begins!    
bot = Bot()
bot.run()