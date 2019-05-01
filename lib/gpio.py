import RPi.GPIO as GPIO
import logging

class GpioHandler:
  """ Start and Stop the Amp """
  def __init__(self,pin,logger=None):
    self.logger = logger or logging.getLogger(__name__)
    self.AmpPin = pin
    self.running = False

    # globals
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(self.AmpPin, GPIO.OUT)
    GPIO.output(self.AmpPin, GPIO.LOW)
    self.logger.info("Init Pin %i" % self.AmpPin)

  def start(self):
    """ starts amp """
    if not self.running:
      GPIO.output(self.AmpPin, GPIO.HIGH)
      self.logger.info("Amp turned on")
      self.running = True

  def stop(self):
    """ stops amp """
    if self.running:
      GPIO.output(self.AmpPin, GPIO.LOW)
      self.logger.info("Amp turned off")
      self.running = False

  def destroy(self):
    self.stop()
    GPIO.cleanup()


