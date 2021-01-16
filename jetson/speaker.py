# -*- coding: utf-8 -*-
"""
スピーカーからメッセージを再生するクラス
"""

from enum import Enum
from playsound import playsound
from contextlib import closing

# 動作モード
class PHRASE(Enum):
	REFIL = 0 # 商品補充して下さい
	UPDATE = 1 # 商品補充が完了しました
	PICKUP = 2 # 商品をお取り下さい
	THANKS = 3 # ご購入ありがとうございました

class Speaker():
	def __init__(self, session, region):
		self.__wav_path = "./wav"
		self.__polly = session.client("polly", region)
	
	# 定型句を再生
	def fixed(self, phrase):
		if(phrase == PHRASE.REFIL):
			playsound("{}/refil_instruction.wav".format(self.__wav_path))
			print("再生：鍵が解錠されました、冷蔵庫を開けて商品補充をして下さい")
		elif(phrase == PHRASE.UPDATE):
			playsound("{}/update_stokck.wav".format(self.__wav_path))
			print("再生：商品補充が完了しました")
		elif(phrase == PHRASE.PICKUP):
			playsound("{}/pick_instruction.wav".format(self.__wav_path))
			print("再生：冷蔵庫を開けて、商品をお取り下さい")
		elif(phrase == PHRASE.THANKS):
			playsound("{}/thanks_to_customer.wav".format(self.__wav_path))
			print("再生：ご購入ありがとうございました")

	# フリーテキストを再生
	def free(self, text):
		response = self.__polly.synthesize_speech(
			Text = text,
			OutputFormat = "mp3",
			VoiceId = "Mizuki")
		if "AudioStream" in response:
			file = open('speech.mp3', 'wb')
			file.write(response['AudioStream'].read())
			file.close()
			playsound("speech.mp3")
