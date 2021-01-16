# -*- coding: utf-8 -*-
"""
OpenCVでWebカメラの画像を取得・表示するクラス
"""

import cv2

class Video:
	def __init__(self, deviceId, width, height):
		GST_STR = ('v4l2src device=/dev/video{} ! video/x-raw, width=(int){}, height=(int){} ! videoconvert ! appsink').format(deviceId, width, height)
		self.__cap = cv2.VideoCapture(GST_STR, cv2.CAP_GSTREAMER)

	def read(self):
		_, frame = self.__cap.read()
		return frame
	
	def show(self, frame):
		cv2.imshow('frame', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			return False
		return True

