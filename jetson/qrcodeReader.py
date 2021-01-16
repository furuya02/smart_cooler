# -*- coding: utf-8 -*-
"""
QRコードリーダの入力を処理するクラス
"""

from pynput.keyboard import Key, Listener
import threading

class QrcodeReader():
	def __init__(self, callback):
		self.__callback = callback
		self.__data = []
		thread = threading.Thread(target=self.__loop)
		thread.start()

	def on_press(self, key):
		if str(key) != 'Key.enter':
			try:
				self.__data.append(key.char[0:1])
			except AttributeError:
				return
		else:
			qr_code = ''.join(self.__data)
			self.__data = []
			self.__callback(qr_code)

	def __loop(self):
		print("start qr reader.")
		with Listener(on_press=self.on_press) as listener:
			listener.join()

