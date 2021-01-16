# -*- coding: utf-8 -*-
"""
DLRによる物体検出モデルの推論クラス
"""

import time
import numpy as np
import os
import cv2
import dlr
import time
import numpy as np
import os
import cv2
from dlr.counter.phone_home import PhoneHome

class Model():
	def __init__(self, names, height, width):
		
		self.__names = names
		# Class数が増える場合は、追加する必要がる
		self.__COLORS = [(0,0,175),(175,0,0),(0,175,0),(175,175,0),(0,175,175),(175,175,175)]

		PhoneHome.disable_feature()
		os.environ['TVM_TENSORRT_CACHE_DIR'] = '.'
		self.__model = dlr.DLRModel('model/', 'gpu', 0)
		print("model OK")

		self.__shape = 512
		self.__h_magnification = self.__shape/height
		self.__w_magnification = self.__shape/width
		print("magnification H:{} W:{}".format(1/self.__h_magnification, 1/self.__w_magnification))


	def inference(self, frame):
		# 入力画像生成
		img = cv2.resize(frame, dsize=(self.__shape, self.__shape)) # height * width => 512 * 512
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # BGR => RGB
		img = img.transpose((2, 0, 1)) # 224,244,3 => 3,224,224
		img = img[np.newaxis, :] # 3,224,224 => 1,3,224,224
		print("img.shape: {}".format(img.shape))

		start = time.time()
		out = self.__model.run({'data' : img})
		elapsed_time = time.time() - start
		print("{} [Sec]".format(elapsed_time))

		result = []
		for det in out[0][0]:
			if(det[0]%1==0 and det[0]!=-1 and det[1] > 0):
				# クラス
				index = int(det[0])
				# 信頼度
				confidence = det[1]
				# 検出座標（縮尺に合わせて座標を変換する）
				x1 = int(det[2] * self.__shape * 1/self.__w_magnification)
				y1 = int(det[3] * self.__shape * 1/self.__h_magnification)
				x2 = int(det[4] * self.__shape * 1/self.__w_magnification)
				y2 = int(det[5] * self.__shape * 1/self.__h_magnification)
				print("[{}] {:.1f} {}, {}, {}, {}".format(self.__names[index], confidence, x1, y1, x2, y2))

				if(confidence > 0.3): # 信頼度
					frame = cv2.rectangle(frame,(x1, y1), (x2, y2), self.__COLORS[index],2)
					frame = cv2.rectangle(frame,(x1, y1), (x1 + 150,y1-20), self.__COLORS[index], -1)
					label = "{} {:.2f}".format(self.__names[index], confidence)
					frame = cv2.putText(frame,label,(x1+2, y1-2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
					result.append(self.__names[index])
		return (result, frame)
