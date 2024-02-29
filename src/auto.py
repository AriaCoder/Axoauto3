# AXOBOTL Python Code
# Extreme Axolotls Robotics team 4028X for 2023-2024 VEX IQ Full Volume Challenge
from vex import *


class Bot:
    MODES = ["MANUAL", "AUTO_RED", "BASKET_2", "BASKET_1", "BASKET_3"]
    MODE_COLORS = [Color.BLACK, Color.RED, Color.YELLOW_GREEN, Color.WHITE, Color.PURPLE]
    MODE_PEN_COLORS = [Color.WHITE, Color.WHITE, Color.BLACK, Color.BLACK, Color.WHITE]

    def __init__(self):
        self.isAutoRunning = False
        self.modeNumber = 0
        self.isManualStarted = False
        self.cancelCalibration = False

    def setup(self):
        self.brain = Brain()
        self.inertial = Inertial()
        self.controller = Controller()
        self.setupPortMappings()
        self.setupDrive()
        self.setupIntake()
        self.setupBasket()
        self.setupController()
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

    def setupController(self):
        self.controller.buttonLUp.pressed(self.onLUp)
        self.controller.buttonLDown.pressed(self.onLDown)
        self.controller.buttonFUp.pressed(self.onFUp)
        self.controller.buttonRUp.pressed(self.onRUp)
        self.controller.buttonRUp.released(self.onRUpReleased)
        self.controller.buttonRDown.pressed(self.onRDown)
        self.controller.buttonRDown.released(self.onRDownReleased)
        # Delay to make sure events are registered correctly.
        wait(15, MSEC)

    def setupSelector(self):
        self.brain.buttonRight.pressed(self.onBrainButtonRight)
        self.brain.buttonLeft.pressed(self.onBrainButtonLeft)
        self.brain.buttonCheck.pressed(self.onBrainButtonCheck)

    def print(self, message):
        screenColor = Bot.MODE_COLORS[self.modeNumber]
        penColor = Bot.MODE_PEN_COLORS[self.modeNumber]
        self.brain.screen.set_font(FontType.MONO20)
        self.brain.screen.set_pen_color(penColor)
        self.brain.screen.set_fill_color(screenColor)
        self.brain.screen.print(message)
        self.brain.screen.new_line()

    def onBrainButtonCheck(self):
        if self.isAutoRunning:
            self.print("Already running")
        else:
            self.isAutoRunning = True
            if self.modeNumber == 1:
                self.runAutoRed()
            elif self.modeNumber == 2:
                self.runBasket2()
            elif self.modeNumber == 3:
                self.runBasket1()
            elif self.modeNumber == 4:
                self.runBasket3()
            #elif self.modeNumber == 5:
               # self.runLeftSide()
            else:
                self.isAutoRunning = False
                self.runManual()
            self.isAutoRunning = False
            self.print("Done")

    def onBrainButtonRight(self):
        self.applyMode(self.modeNumber + 1)

    def onBrainButtonLeft(self):
        self.applyMode(self.modeNumber - 1)

    def applyMode(self, newMode):
        if self.inertial.is_calibrating():
            self.cancelCalibration = True
        if self.isAutoRunning:
            self.print("Running auto already")
        elif self.isManualStarted:
            self.print("In manual mode")
        else:
            self.modeNumber = newMode % len(Bot.MODES)
            self.fillScreen(Bot.MODE_COLORS[self.modeNumber])

    def fillScreen(self, screenColor):
        self.brain.screen.set_pen_color(screenColor)
        self.brain.screen.clear_screen()
        self.brain.screen.set_font(FontType.MONO20)
        self.brain.screen.set_fill_color(screenColor)
        self.brain.screen.draw_rectangle(0, 0, 170, 100, screenColor)
        self.brain.screen.set_cursor(1, 1)
        self.print(Bot.MODES[self.modeNumber])

    def lowerBasket(self):
        if not self.basketDownBumper.pressing():
            # No while loop needed: bumper event handler will get called
            # TODO: Add a timeout, just in case
            self.basket.set_timeout(2, SECONDS)
            self.basket.spin_for(FORWARD, 9000, DEGREES, 100, PERCENT, wait=True)
            self.basket.set_timeout(60, SECONDS)
            self.basket.stop(COAST)
            
    def onLUp(self):
        self.startIntake()
    
    def startIntake(self):
        self.lowerBasket()
        self.intake.spin(FORWARD, 100, PERCENT)

    def onEUp(self):
        pass

    def onLDown(self):
        self.intake.spin(REVERSE, 100, PERCENT)

    def onFUp(self):
        self.stopAll()

    def raiseBasket(self):
        self.intake.stop()
        if not self.basketUpBumper.pressing():           
            self.basket.set_timeout(2, SECONDS)
            self.basket.spin_for(REVERSE, 9000, DEGREES, 100, PERCENT, wait=True)
            self.basket.set_timeout(60, SECONDS)
            self.basket.stop(HOLD)

    def onRUp(self):
        self.raiseBasket()

    def onRUpReleased(self):
        self.basket.stop(HOLD)  # Let blocks fall down, stay put

    def onRDown(self):
        self.lowerBasket()

    def onRDownReleased(self):
        self.basket.stop(HOLD)  # Hold basket in place

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
        if self.driveTrain is not None and not self.isManualStarted:
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
        # Track width: 7-7/8 inches(7.875)
        # Wheel base : 6-1/2 inches(6.5)
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
                and not self.cancelCalibration
                and not self.isManualStarted):
            wait(50, MSEC)
            countdown = countdown - 1
        if self.cancelCalibration or self.isManualStarted:
            self.print("Cancelled Calibration!")
            return False
        elif countdown > 0 and not self.inertial.is_calibrating():
            self.print("Calibrated")
            return True
        else:
            self.stopAll()
            self.print("FAILED Calibration")
            return False
                
    def updateLeftDrive(self, joystickTolerance: int):
        velocity: float = self.controller.axisA.position()
        if math.fabs(velocity) > joystickTolerance:
            self.motorLeft.set_velocity(velocity, PERCENT)
            self.isManualStarted = True
        else:
            self.motorLeft.set_velocity(0, PERCENT)

    def updateRightDrive(self, joystickTolerance: int):
        velocity: float = self.controller.axisD.position()
        if math.fabs(velocity) > joystickTolerance:
            self.motorRight.set_velocity(velocity, PERCENT)
            self.isManualStarted = True
        else:
            self.motorRight.set_velocity(0, PERCENT)

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
        self.runManual()

    def runManual(self):
        i = 0  # start interval 
        self.print("Extreme Axolotls!")
        while(not self.isAutoRunning):
            i += 1 # add interval every 100 milliseconds
            self.updateLeftDrive(5)
            self.updateRightDrive(5)
            if i % 50 == 0: 
                self.checkHealth()  # check health every 5 seconds, using modulus
            sleep(100)

    def runAutoRed(self):
        self.setupAutoDriveTrain(calibrate=False)
        self.intake.spin(REVERSE, 100, PERCENT)
        self.autoDrive(FORWARD, 500, MM, 100, PERCENT, wait=True, timeoutSecs=6)
        self.autoDrive(REVERSE, 500, MM, 100, PERCENT, wait=True)  # Return home

    def runBasket2(self):
        if self.setupAutoDriveTrain():
         self.intake.spin(FORWARD, 100, PERCENT)
         self.autoDrive(FORWARD, 300, MM, 25, PERCENT)
         self.autoTurn(RIGHT, 120, DEGREES, 50, PERCENT)
         self.autoDrive(REVERSE, 600, MM, 50, PERCENT, timeoutSecs=2)
         #self.autoTurn(RIGHT, 28, DEGREES, 50, PERCENT)
         #self.autoDrive(FORWARD, 150, MM, 50 , PERCENT)
         #self.autoTurn(RIGHT, 56, DEGREES, 50, PERCENT, timeoutSecs=2)
         #self.autoDrive(REVERSE, 120, MM, 50, PERCENT, timeoutSecs=2)
         #self.basket.spin_for(REVERSE, 0.9, TURNS)
         #self.basket.set_timeout( 4, SECONDS)
         #self.basket.spin_for(FORWARD, 0.9, TURNS)
         #self.autoDrive(REVERSE, 150, MM, 50, PERCENT)
         #self.autoTurn(LEFT, 45, DEGREES, 50, PERCENT)

        

         #self.autoDrive(REVERSE, 270, MM, 50, PERCENT, wait=True, timeoutSecs=2)
         self.basket.set_timeout(2, SECONDS)
         self.basket.spin_for(REVERSE, 2.5, TURNS)
         self.basket.set_timeout( 4 ,SECONDS)
         
        

        self.stopAll()

    def runBasket1(self):
       if self.setupAutoDriveTrain():
         self.intake.spin(FORWARD, 100, PERCENT)
         self.autoDrive(FORWARD, 140, MM, 25, PERCENT)
         self.autoDrive(REVERSE, 40, MM, timeoutSecs=4)
         self.autoTurn(RIGHT, 42, DEGREES, 45, PERCENT)
         self.autoDrive(REVERSE, 390, MM, 50, PERCENT, timeoutSecs=2)
         self.basket.spin_for(REVERSE, 2.5, TURNS)
         self.basket.set_timeout( 2, SECONDS)

         self.stopAll()

    def runBasket3(self):
       if self.setupAutoDriveTrain():
            self.intake.spin(FORWARD, 100, PERCENT)
            self.autoDrive(FORWARD, 350, MM, 25,PERCENT)
            self.autoDrive(REVERSE, 350, MM, 50, PERCENT)
            self.autoTurn(LEFT, 48, DEGREES, 50 , PERCENT)

            self.autoDrive(REVERSE, 350, MM, 35, PERCENT, timeoutSecs=3)
            self.basket.set_timeout(2, SECONDS)
            self.basket.spin_for(REVERSE, 2.5, TURNS)
            #self.driveTrain.set_timeout(60, SECONDS)
            
            self.stopAll()
       
# Where it all begins!    
bot = Bot()
bot.run()