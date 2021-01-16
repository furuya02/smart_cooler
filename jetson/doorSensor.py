# -*- coding: utf-8 -*-
"""
センサーをGPIO18とGNDに接続して、ドアの開閉を検出するクラス
"""
import time
import threading
import RPi.GPIO as GPIO
from enum import IntEnum

class DOOR_STATUS(IntEnum):
	OPEN = 1
	CLOSED = 0

class DoorSensor:
	def __init__(self, callback):
		GPIO.setmode(GPIO.BCM)
		self.__pin = 18
		GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		self.__callback = callback
		thread = threading.Thread(target=self.__loop)
		thread.start()

	def __loop(self):
		last_status = DOOR_STATUS.OPEN
		last_reads = []

		while(True): 
			if last_status is None:
				last_status = GPIO.input(self.__pin)
			current_status = GPIO.input(self.__pin)
			last_reads.append(current_status)
			last_reads = last_reads[-5:]

			if len(set(last_reads)) > 1:
				time.sleep(0.05)
				continue
			if(last_status != current_status):
				self.__callback(current_status)

			last_status = current_status
			time.sleep(1)
