import os
import sys
import json
import time
import cv2
import numpy as np
from enum import Enum
from cognito import createSession # CognitoのPoolIdでSessionを取得する
from model import Model # DLRによる物体検出モデルの推論クラス
from inventoryManager import InventoryManager # 在庫管理クラス
from video import Video # OpenCVでWebカメラの画像を取得・表示するクラス
from doorSensor import DoorSensor, DOOR_STATUS # センサーをGPIO18とGNDに接続して、ドアの開閉を検出するクラス
from doorLock import DoorLock # ドアをロックするクラス（制御ピン GPIO23）
from qrcodeReader import QrcodeReader # QRコードリーダの入力を処理するクラス
from speaker import Speaker, PHRASE # スピーカーからメッセージを再生するクラス
from amazonPay import AmazonPay # AmazonPayによる決済クラス

# Cognito identity Id
poolId = 'ap-northeast-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
# 商品データベース
tableName = "SmartCoolerProducts"
region = 'ap-northeast-1'
# Webカメラのデバイス番号及び、解像度
deviceId = 0 
width = 800
height = 600

# 動作モード
class MODE(Enum):
	IDLE = 0 # 待機中
	WAIT = 1 # ドアが閉じられるのを待つ
	INFERNCE = 2 # 推論
	PROCESSING = 3 # 処理
	DELAY = 4 # 
	
class Main():
	def __init__(self):
		# 動作モード
		self.__mode = MODE.IDLE
		# メンテナンス（商品追加）モード
		self.__isMentenance = False
		# Session取得
		session = createSession(poolId, region)
		# 在庫管理
		self.__inventoryManager = InventoryManager(session, region, tableName)
		# AmazonPay
		self.__amazonPay = AmazonPay(session, region)
		# 商品検出モデル
		self.__model = Model(self.__inventoryManager.short_names, height, width)
		# カメラ映像
		self.__video = Video(deviceId, width, height)
		# ドアのロック
		self.__doorLock = DoorLock()
		# スピーカー
		self.__speaker = Speaker(session, region)
		# ドアの開閉検出
		DoorSensor(self.__on_change_door_status)
		# QRコードリーダー
		QrcodeReader(self.__on_read_qr_code)

		self.__run()

	# 動作モードの変更
	def __setMode(self, mode):
		self.__mode = mode
		print("---------------------------------------")
		print("{}".format(self.__mode))
		print("---------------------------------------")
	
	# 推論処理
	def __inference(self):
		print("model.inference frame:{}".format(self.__frame.shape))
		(result, self.__frame) = self.__model.inference(self.__frame)
		print("冷蔵庫内の商品  {}".format(result))
		return result
	
	# AmazonPayでのQRコード確認 chargePermissionId取得
	def __check_qr_code(self, scanData):
		responce = self.__amazonPay.scan(scanData)
		if(responce["statusCode"] == 200):
			return responce["body"]["chargePermissionId"]
		return None
	
	# AmazonPayでの購入処理
	def __purchase(self, chargePermissionId, amount):
		amount = amount
		merchantNote = "note"
		merchantStoerName = "classMethod"
		merchantOrderId = "orderId"
		response = self.__amazonPay.charge(chargePermissionId, amount, merchantNote, merchantStoerName, merchantOrderId)
		if(response["statusCode"] == 200):
			return True
		return False

	# ドアの開閉の変化
	def __on_change_door_status(self, status):
		str = "ドアが、開けられました" if status == DOOR_STATUS.OPEN else "ドアが、閉じられました"
		print(str)

		# ドアが閉じられた時
		if(status == DOOR_STATUS.CLOSED):
			# ドアをロックする
			print("ドアロック")
			self.__doorLock.enable() 
			if(self.__mode == MODE.WAIT):
				# 推論処理へ
				self.__setMode(MODE.INFERNCE)

	# QRコードの読み込み
	def __on_read_qr_code(self, qr_code):
		print("QRコードが読み込まれました: {}".format(qr_code))
		
		# メンテナンス用のコードかどうかの判定
		self.__isMentenance = False
		if (qr_code == "123456"):
			print("メンテナンスモード")
			self.__isMentenance = True
		else:
			# 有効なQRコードかどうかの判定
			self.__chargePermissionId = self.__check_qr_code(qr_code)
			if(self.__chargePermissionId == None):
				print("QRコードが無効")
				return
		print("ドアロック解除")
		self.__doorLock.disable() 
		self.__setMode(MODE.WAIT)
		
		if(self.__isMentenance):
			self.__speaker.fixed(PHRASE.REFIL)
		else:
			self.__speaker.fixed(PHRASE.PICKUP)

	# メインループ
	def __run(self):
		while(True):
			# MODE.DELAY中だけ、画像を更新しない
			if(self.__mode != MODE.DELAY):
				self.__frame = self.__video.read()
				if(self.__frame is None):
					continue
			
			# 推論処理
			if(self.__mode == MODE.INFERNCE):
				result = self.__inference()
				self.__setMode(MODE.PROCESSING)

			# PROCESSINGモードで処理を行う
			if(self.__mode == MODE.PROCESSING):

				# 変更前の在庫
				before_stock = self.__inventoryManager.getStock()
				# 在庫数変更
				self.__inventoryManager.setStock(result)
				# 変更後の在庫
				after_stock = self.__inventoryManager.getStock()

				if(self.__isMentenance):
					self.__speaker.fixed(PHRASE.UPDATE)
				else:
					# 減少分のカウント
					diff = []
					for index in range(len(before_stock)):
						diff.append(before_stock[index] - after_stock[index])
				
					anount = 0
					items = []
					text = "お買い上げは、"
					for index in range(len(diff)):
						if(diff[index] != 0):
							full_name = self.__inventoryManager.get_full_name(index)
							price = self.__inventoryManager.get_price(index)
							items.append(" >> {} {}円 {}個".format(full_name, price, diff[index]))
							text += "{} {}円 {}個、".format(full_name, price, diff[index])
							anount += price * diff[index]
					if(anount != 0):
						
						print("\n >> 取り出された商品は、以下のとおりです\n")
						for item in items:
							print(item)
						print("\n >> 合計{}円\n".format(anount))

						text += "合計で、{}円です。".format(anount)
						self.__speaker.free(text)
						
						# 購入処理
						if self.__purchase(self.__chargePermissionId, anount):
							print("AmazonPayの購入処理を完了")
							self.__speaker.fixed(PHRASE.THANKS)
						else:
							print("AmazonPayの購入処理に失敗")
	
				# MODE.DELAYで10秒間待機
				self.__setMode(MODE.DELAY)
				self.__delay_counter = 10

			
			if(self.__mode == MODE.DELAY):
				print("DELAY {}".format(self.__delay_counter))
				self.__delay_counter -= 1
				time.sleep(1)
				if(self.__delay_counter <= 0):
					print("待機中")
					self.__setMode(MODE.IDLE)

			# 画像表示　終了キー'q'が押された場合Falseが返される
			if(self.__video.show(self.__frame) == False):
				break

Main()
