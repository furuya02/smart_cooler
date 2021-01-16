# -*- coding: utf-8 -*-
"""
ドアをロックするクラス（制御ピン GPIO23）
"""

import RPi.GPIO as GPIO
from enum import IntEnum

class DoorLock:
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		self.__pin = 23
		GPIO.setup(self.__pin, GPIO.OUT)
		self.enable()
	
	def enable(self):
		GPIO.output(self.__pin, GPIO.LOW)

	def disable(self):
		GPIO.output(self.__pin, GPIO.HIGH)
