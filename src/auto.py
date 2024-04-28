# AXOBOTL Python Code
# Extreme Axolotls Robotics team 4028X for 2023-2024 VEX IQ Full Volume Challenge
from vex import *


class Bot:
    MODES = ["AUTO_RED", "GOAL_2", "GOAL_1", "GOAL_3", "CURVE"]
    MODE_COLORS = [Color.RED, Color.YELLOW_GREEN, Color.WHITE, Color.PURPLE, Color.YELLOW]
    MODE_PEN_COLORS = [Color.WHITE, Color.BLACK, Color.BLACK, Color.WHITE, Color.BLACK]

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
        self.setupBasket()
        self.setupSelector()

    def setupPortMappings(self):
        self.motorLeft = Motor(Ports.PORT1,1,True)
        self.motorRight = Motor(Ports.PORT6,1, False)
        self.intakeLeft = Motor(Ports.PORT3,1,True)
        self.intakeRight = Motor(Ports.PORT7)
        self.basketLeft = Motor(Ports.PORT8)
        self.basketRight = Motor(Ports.PORT2)
        self.healthLed = Touchled(Ports.PORT9)
        self.basketDownBumper = Bumper(Ports.PORT4)
        self.basketUpBumper = Bumper(Ports.PORT5)
        self.driveTrain = None  # Default is MANUAL mode, no driveTrain

    def setupIntake(self):
        self.intake = MotorGroup(self.intakeLeft, self.intakeRight)
        self.intake.set_velocity(100, PERCENT)

    def setupBasket(self):
        self.basketLeft.set_reversed(True)
        self.basket = MotorGroup(self.basketLeft, self.basketRight)
        self.basket.set_velocity(100, PERCENT)
        self.basketUpBumper.pressed(self.onBasketUpBumper)
        self.basketDownBumper.pressed(self.onBasketDownBumper)

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
                self.runAutoRed()
            elif self.modeNumber == 1:
                self.runGoal2()
            elif self.modeNumber == 2:
                self.runGoal1()
            elif self.modeNumber == 3:
                self.runGoal3()
            elif self.modeNumber == 4:
                self.runCurveHome()
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
        self.lowerBasket()
        self.intake.spin(REVERSE, 100, PERCENT)

    def raiseBasket(self, turns: float = 0.0):
        self.intake.stop()
        if not self.basketUpBumper.pressing():           
            self.basket.set_timeout(2, SECONDS)
            if turns != 0.0:
                self.basket.spin_for(FORWARD, turns, TURNS, 100, PERCENT, wait=True)
            else:
                self.basket.spin_for(FORWARD, 9000, DEGREES, 100, PERCENT, wait=True)
            self.basket.set_timeout(60, SECONDS)
            self.basket.stop(HOLD)

    def lowerBasket(self, turns: float = 0.0, wait: bool = True):
        if not self.basketDownBumper.pressing():
            # No while loop needed: bumper event handler will get called
            # TODO: Add a timeout, just in case
            self.basket.set_timeout(2, SECONDS)
            if turns != 0.0:
                self.basket.spin_for(REVERSE, turns, TURNS, 100, PERCENT, wait)
            else:
                self.basket.spin_for(REVERSE, 9000, DEGREES, 100, PERCENT, wait=wait)
            if wait:
                self.basket.set_timeout(60, SECONDS)
                self.basket.stop(COAST)

    def onBasketUpBumper(self):
        self.basket.stop(COAST)

    def onBasketDownBumper(self):
        self.basket.stop(COAST)

    def setupDrive(self):
        self.motorLeft.set_velocity(0, PERCENT)
        self.motorLeft.set_max_torque(100, PERCENT)
        self.motorLeft.spin(REVERSE)
        self.motorRight.set_velocity(0, PERCENT)
        self.motorRight.set_max_torque(100, PERCENT)
        self.motorRight.spin(REVERSE)

    def stopAll(self):
        if self.driveTrain:
            self.driveTrain.stop(COAST)
        self.intake.stop(COAST)
        self.basket.stop(COAST)

    def checkHealth(self):
        # Copied from our code for Slapshot 2022-23 season
        color = Color.RED
        capacity = self.brain.battery.capacity()
        if capacity > 95:
            color = Color.BLUE
        elif capacity > 85:
            color = Color.GREEN
        elif capacity > 81:
            color = Color.ORANGE
        else:
            self.print("Battery level is too low for auton")
            color = Color.RED
        self.healthLed.set_color(color)

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
    def autoBasket(self, up: bool = True):
        self.basket.set_timeout(3000, MSEC)
        # Let the up/down basket bumpers take care of stopping the basket
        if up:
            self.basket.spin_for(REVERSE, 9000, RotationUnits.DEG, 100, PERCENT)
        else:
            self.basket.spin_for(FORWARD, 9000, RotationUnits.DEG, 100, PERCENT)

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

    def autoDump(self):
        #wait(1, SECONDS)
        self.raiseBasket(turns=5)
        wait(1, SECONDS)
        self.lowerBasket(turns=6, wait=False) # Faster if we don't wait

    def runAutoRed(self):
        self.setupAutoDriveTrain(calibrate=False)
        self.intake.spin(REVERSE, 100, PERCENT)
        self.autoDrive(FORWARD, 500, MM, 100, PERCENT, wait=True, timeoutSecs=6)
        self.autoDrive(REVERSE, 500, MM, 100, PERCENT, wait=True)  # Return home

    def runGreenStrip(self):
        self.startIntake()
        self.autoDrive(FORWARD, 360, MM, 40, PERCENT)
        self.autoDrive(REVERSE, 260, MM, 50, PERCENT)
        
    def runGoal2(self):
        # Grab greens from line
        self.runGreenStrip()
        
        # Corner shot
        self.autoTurn(RIGHT, 30, DEGREES, 45, PERCENT, timeoutSecs=2)
        self.autoDrive(REVERSE, 140, MM, 50, PERCENT, timeoutSecs=1)

        # Wiggle-wiggle
        #self.autoTurn(RIGHT, 20, DEGREES, 100, PERCENT,timeoutSecs=1)
        #self.autoTurn(LEFT, 20, DEGREES, 100, PERCENT,timeoutSecs=1)

        # Score 4 blocks
        self.autoDump()

        # Goes back in position
        self.startIntake()
        self.autoDrive(FORWARD, 80, MM, 70, PERCENT, timeoutSecs=2)
       # self.autoDrive(REVERSE, 560, MM, 100, PERCENT, timeoutSecs=2)

        # Use wall as checkpoint, go back to starting position
        self.autoTurn(LEFT, 35, DEGREES, 50, PERCENT, timeoutSecs=1)
        self.autoDrive(REVERSE, 300, MM, 110, PERCENT, timeoutSecs=1)

        self.finishCheckpoint()
        self.runGoal1()
        return
    
    def runGoal1(self):
        self.startIntake()

        # Run across line, spin around to face flower and hit red
        self.autoDrive(FORWARD, 360, MM, 70, PERCENT, timeoutSecs=2)
        self.autoTurn(LEFT, 85, DEGREES, 50, PERCENT, timeoutSecs=2)
    
        # Grab Flower and Wall Slide to goal
        self.autoDrive(FORWARD, 300, MM, 50, PERCENT, timeoutSecs=2)
        self.autoTurn(LEFT,50, DEGREES, 100, PERCENT, timeoutSecs=2)
        self.autoDrive(REVERSE, 450, MM, 100, PERCENT, timeoutSecs=2)
        wait(1, SECONDS) # Let the intake run to bring in blocks
         
        # Score about 6 blocks?
        self.autoDump()
        
        # Next checkpoint
        self.finishCheckpoint()

        # Risky: Run across the field, or less risky: go home
        if True:
            self.runCurveHome()
        else:
            self.runCurveOut()
        return
    
    def runCurveOut(self):
        self.startIntake()
        self.autoDrive(FORWARD, 105, MM, 50, PERCENT, timeoutSecs=1 )
        self.autoArc(105, 15, 80, 4)
        self.autoDrive(FORWARD, 620, MM, 80)
        self.autoTurn(RIGHT, 100, DEGREES)
        self.autoDrive(FORWARD, 400, MM)

        # TODO: Cross the whole field and go for the 2nd line of greens
        self.finishCheckpoint()
        return
    
    def runCurveHome(self):
        self.autoArc(160, 20, 100, 4)
        self.autoDrive(FORWARD, 200, MM, 100, timeoutSecs=2)  # go forward a bit
        self.autoArc(140, 20, 100, 3)
        self.autoDrive(FORWARD, 500, MM, 100, timeoutSecs=2)  # Wall slide
        self.stopAll()
        self.finishCheckpoint()
        self.finishRun()
        return
    
    def runGoal3(self):
        self.intake.spin(FORWARD, 100, PERCENT)
        self.autoDrive(FORWARD, 350, MM, 25,PERCENT)
        self.autoDrive(REVERSE, 350, MM, 50, PERCENT)
        self.autoTurn(LEFT, 52, DEGREES, 100 , PERCENT)
        self.autoDrive(REVERSE, 350, MM, 100, PERCENT, timeoutSecs=3)
        self.basket.set_timeout(2, SECONDS)
        self.basket.spin_for(REVERSE, 2.5, TURNS)
        self.stopAll()
       

    def runGoal3New(self):
        self.autoBasket(up=False)
        self.runGreenStrip()
        self.autoDrive(FORWARD, 180, MM, 50, timeoutSecs=2)

        # Curve to avoid backing into the purple flower
        self.autoArc(300, -80, 15, timeoutSecs=3)

        # Hit the right wall at an angle
        self.autoDrive(REVERSE, 250, MM, 100, timeoutSecs=2)
        self.autoTurn(RIGHT, 20, DEGREES, 50, PERCENT, timeoutSecs=1)

        # Turn to pick up some green from the flower
        self.autoArc(330, 80, 15, timeoutSecs=3)
        self.autoDrive(FORWARD, 200, MM, velocity=50, timeoutSecs=1)

        # Wait a bit to digest
        wait(1, SECONDS)

        # Drive fast toward the wall and goal
        self.autoArc(300, -80, -10, timeoutSecs=2)
        self.autoDump()

        self.stopAll()
        self.finishCheckpoint()
    
        
# Where it all begins!    
bot = Bot()
bot.run()